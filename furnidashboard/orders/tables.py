import django_tables2 as tables
from django_tables2.utils import A #accessor
from .models import Order

class UnplacedOrdersTable(tables.Table):
  created = tables.TemplateColumn('{{ record.created|date:\'m/d/Y\'}}') 
  detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">View Detail</a>', verbose_name="Actions")

  class Meta:
    model = Order
    attrs = {"class": "important"}
    fields = ("number", "created", "customer", "detail")

class OrderTable(tables.Table):
  #id = tables.Column() #LinkColumn("order_edit", args=[A("pk")], verbose_name='Detail', empty_values=())
  created = tables.TemplateColumn('{{ record.created|date:\'m/d/Y\'}}') 
  modified = tables.TemplateColumn('{{ record.modified|date:\'m/d/Y\'}}', verbose_name="Last Modified") 
  detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions")

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "created", "customer", "grand_total", "status","modified", "detail")
