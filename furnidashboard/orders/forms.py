from stores.models import Store
from .models import Order, OrderItem
from commissions.models import Commission
from customers.models import Customer
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from ajax_select.fields import AutoCompleteSelectField
from bootstrap_toolkit.widgets import BootstrapDateInput

CommissionFormSet = inlineformset_factory(Order, Commission, extra=1, max_num=1, can_delete=False)
CustomerFormSet = modelformset_factory(Customer, extra=1, max_num=1)

class OrderItemForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(OrderItemForm, self).__init__(*args, **kwargs)
    self.fields['in_stock'].widget.attrs['class'] = "order-item-in-stock"
    self.fields['description'].widget.attrs['class'] = "order-item-desc"
    self.fields['po_num'].widget.attrs['class'] = "order-item-po"
    self.fields['po_date'].widget.attrs['class'] = "order-item-po-date"
    self.fields['ack_num'].widget.attrs['class'] = "order-item-ack-num"
    self.fields['ack_date'].widget=BootstrapDateInput()
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
    
    
  class Meta:
    pass
    model = Order

ItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, max_num=100)

def get_ordered_items_formset(extra=1, max_num=1000):
  return inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=extra, max_num=max_num)