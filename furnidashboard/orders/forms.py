from stores.models import Store
from .models import Order, OrderItem
from commissions.models import Commission
from customers.models import Customer
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

CommissionFormSet = inlineformset_factory(Order, Commission, extra=1, max_num=1, can_delete=False)
CustomerFormSet = modelformset_factory(Customer, extra=1, max_num=1)
ItemFormSet = inlineformset_factory(Order, OrderItem, extra=1)

class OrderForm(forms.ModelForm):
  class Meta:
    model = Order
    #fields=('number', 'status', 'deposit_balance', 'subtotal_after_discount', 'tax', 'shipping', 'comments', 'store')


