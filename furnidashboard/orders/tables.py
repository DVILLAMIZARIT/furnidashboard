import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A #accessor
from .models import Order, OrderDelivery

class CustomTextLinkColumn(tables.LinkColumn):
  def __init__(self, viewname, urlconf=None, args=None, kwargs=None, current_app=None, attrs=None, custom_text=None, **extra):
    super(CustomTextLinkColumn, self).__init__(viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app, attrs=attrs, **extra)
    self.custom_text = custom_text

  def render(self, value, record, bound_column):
    return super(CustomTextLinkColumn, self).render(self.custom_text if self.custom_text else value, record, bound_column)

class AssociateColumn(tables.Column):
  def render(self, value):
    commissions = value.all()
    associates = ", ".join([comm.associate.first_name for comm in commissions])
    return mark_safe(associates)

class OrderTable(tables.Table):
  created = tables.TemplateColumn('{{ record.created|date:\'m/d/Y\'}}') 
  modified = tables.TemplateColumn('{{ record.modified|date:\'m/d/Y\'}}', verbose_name="Last Modified") 
  # detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions", orderable=False)
  number  = tables.LinkColumn('order_detail', orderable=False, kwargs={'pk': A('pk')})
  associate = AssociateColumn(accessor="commission_set", verbose_name="Associate")
  grand_total = tables.Column(orderable=False)

  def render_number(self, record):
    return "Edit"

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "created", "status", "store", "customer", "grand_total", "modified", "associate")

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

class DeliveriesTable(tables.Table):
  order = tables.LinkColumn('order_detail', args=[A('order.pk')])
  pk = CustomTextLinkColumn('delivery_detail', args=[A('pk')], custom_text="Detail", orderable=False, verbose_name="Actions")

  class Meta:
    model = OrderDelivery
    attrs = {"class":"paleblue"}
    fields = ("order", "scheduled_delivery_date", "delivery_type", 'delivered_date') 
