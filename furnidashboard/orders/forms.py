from stores.models import Store
from .models import Order, OrderItem, OrderDelivery
from commissions.models import Commission
from customers.models import Customer
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth import get_user_model
from ajax_select.fields import AutoCompleteSelectField
from bootstrap_toolkit.widgets import BootstrapDateInput
from core.mixins import DisabledFieldsMixin
from django.db.models import Q
import core.utils as utils

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

  class Meta:
      model = OrderItem

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
    super(CommissionForm, self).__init__(*args, **kwargs)
    self.fields['paid_date'].widget = BootstrapDateInput()
    self.fields['associate'].required = True
    user_model = get_user_model() 
    self.fields['associate'].queryset = user_model.objects.filter(Q(groups__name__icontains="associates") | Q(groups__name__icontains="managers" ))

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

def get_commissions_formset(extra=1, max_num=1000):
  return inlineformset_factory(Order, Commission, form=CommissionForm, extra=extra, max_num=max_num, can_delete=False)

ItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, max_num=100)
DeliveryFormSet = inlineformset_factory(Order, OrderDelivery, form=OrderDeliveryForm, extra=1, max_num=100)
CommissionFormSet = inlineformset_factory(Order, Commission, form=CommissionForm, extra=1, max_num=100, can_delete=False)
CustomerFormSet = modelformset_factory(Customer, form=CustomerForm, extra=1, max_num=1)
