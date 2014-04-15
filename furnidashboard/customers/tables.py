import django_tables2 as tables
from django_tables2.utils import A #accessor
from orders.models import Order, OrderDelivery
from .models import Customer
from core.tables import CustomTextLinkColumn

class CustomersTable(tables.Table):
  pk = CustomTextLinkColumn('customer_detail', args=[A('pk')], custom_text="More Info", orderable=False, verbose_name="Actions")

  class Meta:
    model = Customer
    attrs = {"class":"paleblue"}
    fields = ("first_name", "last_name", "email", "phone", "pk") 
