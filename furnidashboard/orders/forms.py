from stores.models import Store
from .models import Order, OrderItem
from commissions.models import Commission
from customers.models import Customer
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

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
    self.fields['ack_date'].widget.attrs['class'] = "order-item-ack-date"
    self.fields['eta'].widget.attrs['class'] = "order-item-eta"
    self.fields['eta'].label = "ETA"
    #import pdb; pdb.set_trace()
    self.fields['description'].widget.attrs['size']=80


  class Meta:
      model = OrderItem

class OrderForm(forms.ModelForm):
  class Meta:
    model = Order
    #fields=('number', 'status', 'deposit_balance', 'subtotal_after_discount', 'tax', 'shipping', 'comments', 'store')

ItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, max_num=100)

