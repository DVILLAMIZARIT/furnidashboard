import django_tables2 as tables
from django_tables2.utils import A #accessor
from .models import Order

class OrderTable(tables.Table):
  #id = tables.Column() #LinkColumn("order_edit", args=[A("pk")], verbose_name='Detail', empty_values=())
  created = tables.TemplateColumn('{{ record.created|date}}') 
  modified = tables.TemplateColumn('{{ record.modified|date}}', verbose_name="Last Modified") 
  edit = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>')

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "created", "customer", "grand_total", "status","modified", "edit")
