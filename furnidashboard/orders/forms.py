from stores.models import Store
from .models import Order, OrderItem, OrderDelivery
from commissions.models import Commission
from customers.models import Customer
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth import get_user_model
from django.utils.functional import curry
from ajax_select.fields import AutoCompleteSelectField
from bootstrap_toolkit.widgets import BootstrapDateInput
from core.mixins import DisabledFieldsMixin
from django.db.models import Q
import core.utils as utils
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field
from crispy_forms.bootstrap import AppendedText

class OrderItemForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(OrderItemForm, self).__init__(*args, **kwargs)
    self.fields['in_stock'].widget.attrs['class'] = "order-item-in-stock"
    self.fields['description'].widget.attrs['class'] = "order-item-desc"
    self.fields['description'].required = True
    self.fields['po_num'].widget.attrs['class'] = "order-item-po"
    self.fields['po_num'].label = "PO #"
    self.fields['po_date'].widget = BootstrapDateInput()
    self.fields['po_date'].label = "PO placed date"
    self.fields['po_date'].widget.attrs['class'] = "order-item-po-date"
    self.fields['ack_num'].widget.attrs['class'] = "order-item-ack-num"
    self.fields['ack_num'].label = "Acknowledgement #"
    self.fields['ack_date'].widget=BootstrapDateInput()
    self.fields['ack_date'].label = "Acknowl. date"
    self.fields['ack_date'].widget.attrs['class'] = "order-item-ack-date"
    
    self.fields['eta'].widget=BootstrapDateInput()    
    self.fields['eta'].widget.attrs['class'] = "order-item-eta"
    self.fields['eta'].label = "ETA"
    #import pdb; pdb.set_trace()
    self.fields['description'].widget.attrs['size']=80

    # self.helper = FormHelper()
#    self.helper.layout = Layout(
#      Div(
#        'description',
#        'in_stock',
#        css_class='item-general-fields',
#      ),
#      Div(
#        'status', 
#        Div(
#          Field('po_num'),
#          AppendedText('po_date', '<i class="icon-calendar"></i>'), 
#          css_class='form-inline',
#        ),
#        Div(
#          'ack_num', 
#          AppendedText('ack_date', '<i class="icon-calendar"></i>'),
#        ),
#        AppendedText('eta', '<i class="icon-calendar"></i>'),
#        css_class='item-special-fields',
#      ),
#    )

  def clean(self):
    cleaned_data = super(OrderItemForm, self).clean()
    status = cleaned_data.get("status")
    if status in ('O', 'R', 'D'): #ordered, received, or delivered
      #check that all ordered items have PO num and date
      po_num = cleaned_data.get('po_num')
      po_date = cleaned_data.get('po_date')
      if po_num == None or po_date == None:
        #raise forms.ValidationError("Specify PO number and PO entered date before changing item status to 'Ordered'")
        msg = "Specify PO# and PO date before changing item status"
        # self.add_error('status', msg)
        raise forms.ValidationError(msg)

    return cleaned_data

  class Meta:
    model = OrderItem
    #fields = ['description', 'in_stock', 'status', 'po_num', 'po_date', 'ack_num', 'ack_date', 'eta']

class OrderItemFormHelper(FormHelper):
  def __init__(self, *args, **kwargs):
    super(OrderItemFormHelper, self).__init__(*args, **kwargs)
    self.form_tag = False
    self.disable_csrf = True
    self.layout = Layout(
      Div(
        'description',
        'in_stock',
        css_class='item-general-fields',
      ),
      Div(
        'status', 
        Div(
          Field('po_num'),
          AppendedText('po_date', '<i class="icon-calendar"></i>'), 
          css_class='form-inline',
        ),
        Div(
          'ack_num', 
          AppendedText('ack_date', '<i class="icon-calendar"></i>'),
        ),
        AppendedText('eta', '<i class="icon-calendar"></i>'),
        css_class='item-special-fields',
      ),
    )


class OrderForm(forms.ModelForm):
  customer = AutoCompleteSelectField('customer', required=False)
  
  def __init__(self, *args, **kwargs):
    super(OrderForm, self).__init__(*args, **kwargs)
    self.fields['status'].initial='N'
    self.fields['created'].widget = BootstrapDateInput()
    self.fields['created'].label = "Ordered Date"
    self.fields['created'].widget.attrs['class'] = "order-date"

  class Meta:
    model = Order

class CommissionForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    super(CommissionForm, self).__init__(*args, **kwargs)
    self.fields['paid_date'].widget = BootstrapDateInput()
    self.fields['associate'].required = True
    user_model = get_user_model() 
    self.fields['associate'].queryset = user_model.objects.filter(Q(groups__name__icontains="associates") | Q(groups__name__icontains="managers" ))
    
    if self.request and not self.request.user.has_perm('commissions.update_commissions_payment'):
      # person can modify only certain delivery info data
      self.fields['paid_date'].widget.attrs['disabled'] = 'disabled'
      self.fields['paid'].widget.attrs['disabled'] = 'disabled'

  class Meta:
     model = Commission

class OrderDeliveryForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    super(OrderDeliveryForm, self).__init__(*args, **kwargs)
    self.fields['scheduled_delivery_date'].widget = BootstrapDateInput()
    self.fields['delivered_date'].widget = BootstrapDateInput()
    
    if self.request and utils.is_user_delivery_group(self.request):
      # person can modify only certain delivery info data
      enabled_fields = ('delivered_date', 'comments')
      remove = [f for f in self.fields if f not in enabled_fields]
      for field in remove: 
          del self.fields[field]
  
  class Meta:
    model = OrderDelivery

class CustomerForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(CustomerForm, self).__init__(*args, **kwargs)

  class Meta:
    model = Customer

class CustomerDetailReadOnlyForm(DisabledFieldsMixin, CustomerForm):
  def __init__(self, *args, **kwargs):
    super(CustomerDetailReadOnlyForm, self).__init__(*args, **kwargs)


def get_ordered_items_formset(extra=1, max_num=1000):
  return inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=extra, max_num=max_num)

def get_deliveries_formset(extra=1, max_num=1000):
  return inlineformset_factory(Order, OrderDelivery, form=OrderDeliveryForm, extra=extra, max_num=max_num)

def get_commissions_formset(extra=1, max_num=1000, request=None):
  formset = inlineformset_factory(Order, Commission, extra=extra, max_num=max_num, can_delete=False)
  formset.form = staticmethod(curry(CommissionForm, request=request))  
  return formset

ItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, max_num=100)
DeliveryFormSet = inlineformset_factory(Order, OrderDelivery, form=OrderDeliveryForm, extra=1, max_num=100)
CommissionFormSet = inlineformset_factory(Order, Commission, form=CommissionForm, extra=1, max_num=100, can_delete=False)
CustomerFormSet = modelformset_factory(Customer, form=CustomerForm, extra=1, max_num=1)
