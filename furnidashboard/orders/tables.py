import django_tables2 as tables
from django_tables2.utils import A #accessor
from .models import Order

class OrderTable(tables.Table):
  id = tables.LinkColumn("order_edit", args=[A("pk")], verbose_name='Detail', empty_values=(), title="Edit")

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "created", "modified", "customer", "status", "id")