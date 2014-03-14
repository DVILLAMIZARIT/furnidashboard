import django_tables2 as tables
from django_tables2.utils import A #accessor
from .models import Order

class OrderTable(tables.Table):
  action = tables.LinkColumn("order_delete", args=[A("id")])

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
