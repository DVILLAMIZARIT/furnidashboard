import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A #accessor
from .models import Order

class AssociateColumn(tables.Column):
  def render(self, value):
    commissions = value.all()
    associates = ", ".join([comm.associate.first_name for comm in commissions])
    return mark_safe(associates)

class OrderTable(tables.Table):
  #id = tables.Column() #LinkColumn("order_edit", args=[A("pk")], verbose_name='Detail', empty_values=())
  created = tables.TemplateColumn('{{ record.created|date:\'m/d/Y\'}}') 
  modified = tables.TemplateColumn('{{ record.modified|date:\'m/d/Y\'}}', verbose_name="Last Modified") 
  detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions", orderable=False)
  associate = AssociateColumn(accessor="commission_set", verbose_name="Associate")
  grand_total = tables.Column(orderable=False)

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "created", "status", "store", "customer", "grand_total", "modified", "associate", "detail")

class UnplacedOrdersTable(tables.Table):

  created = tables.TemplateColumn('{{ record.created|date:\'m/d/Y\'}}') 
  detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions", orderable=False)
  associate = AssociateColumn(accessor="commission_set", verbose_name="Associate")
  grand_total = tables.Column(orderable=False)

  class Meta:
    model = Order
    attrs = {"class": "paleblue urgent"}
    fields = ("number", "created", "customer", "grand_total", "associate", "detail")

class SalesByAssociateTable(tables.Table):
  associate = tables.Column()
  sales = tables.Column()

  class Meta:
    attrs = {"class":"paleblue"}
