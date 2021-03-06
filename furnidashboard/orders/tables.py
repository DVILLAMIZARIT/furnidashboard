import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A #accessor
from .models import Order, OrderDelivery
from core.tables import CustomTextLinkColumn
import core.utils as utils

class OrderAssociatesColumn(tables.Column):
  empty_values = ()
  def render(self, value, record):
    commissions = record.commission_set.all()  
    associates = ", ".join([comm.associate.first_name for comm in commissions])
    return mark_safe(associates)

class AssociateNameColumn(tables.Column):
  def render(self, value):
    return mark_safe("{0} {1}".format(value.first_name, value.last_name))

class DollarAmountColumn(tables.Column):
  def render(self, value):
    return utils.dollars(value)

class OrderTable(tables.Table):
  order_date = tables.TemplateColumn('{{ record.order_date|date:\'m/d/Y\'}}') 
  modified = tables.TemplateColumn('{{ record.modified|date:\'m/d/Y\'}}', verbose_name="Last Modified") 
  # detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions", orderable=False)
  pk = CustomTextLinkColumn('order_detail', args=[A('pk')], custom_text="Detail", orderable=False, verbose_name="Actions")
  associate = OrderAssociatesColumn(accessor="pk", verbose_name="Associate")
  subtotal_after_discount = DollarAmountColumn(verbose_name="Subtotal")
  grand_total = DollarAmountColumn(orderable=False)

  class Meta:
    model = Order
    attrs = {"class": "paleblue"}
    fields = ("number", "order_date", "status", "store", "customer", "subtotal_after_discount", "grand_total", "modified", "associate")

class UnplacedOrdersTable(tables.Table):

  order_date = tables.TemplateColumn('{{ record.order_date|date:\'m/d/Y\'}}') 
  detail = tables.TemplateColumn('<a href="{% url \'order_detail\' record.pk %}">Detail</a>', verbose_name="Actions", orderable=False)
  associate = OrderAssociatesColumn(accessor="record.pk", verbose_name="Associate")
  grand_total = tables.Column(orderable=False)

  class Meta:
    model = Order
    attrs = {"class": "paleblue urgent"}
    fields = ("number", "order_date", "customer", "grand_total", "associate", "detail")

class SalesByAssociateTable(tables.Table):
  associate = tables.Column(orderable=False)
  sales = DollarAmountColumn(verbose_name="Sales (Subtotal after discount)")
  commissions_paid = DollarAmountColumn(verbose_name="Commissions Paid")
  commissions_pending = DollarAmountColumn(verbose_name="Commissions Pending")
  commissions_due = DollarAmountColumn(verbose_name="Commissions Due")

  class Meta:
    order_by='-sales'
    attrs = {"class":"paleblue sales-table"}

class SalesByAssocSalesTable(tables.Table):
  order_number = tables.Column(verbose_name="Order #")
  order_date = tables.Column(verbose_name="Order date")
  item = tables.Column(verbose_name="Sold items")
  amount = DollarAmountColumn(verbose_name="Order Subtotal")
  commissions_paid = DollarAmountColumn(verbose_name="Commissions Paid")
  commissions_pending = DollarAmountColumn(verbose_name="Commissions Pending")
  commissions_due = DollarAmountColumn(verbose_name="Commissions Due")
  order_pk = CustomTextLinkColumn('order_detail', args=[A('order_pk')], custom_text="Details", orderable=False, verbose_name="Actions")

  class Meta:
    order_by='-order_date'
    attrs = {"class":"paleblue"}


class SalesByAssociateWithBonusTable(tables.Table):
  associate = tables.Column(orderable=False)
  sales = DollarAmountColumn()
  bonus = DollarAmountColumn(verbose_name="Bonus amount")

  class Meta:
    order_by='-sales'
    attrs = {'class':'paleblue'}

class UnpaidCommissionsTable(tables.Table):
  associate = AssociateNameColumn(verbose_name="Associate")
  order_date = tables.Column()
  order = tables.Column()
  order_total = DollarAmountColumn()
  commissions_due = DollarAmountColumn(verbose_name="Commissions Due")

  def render_order(self, value):
    return mark_safe('<a href="{0}">#{1}</a>'.format(value.get_absolute_url(), str(value)))

  class Meta:
    order_by='order_date'
    attrs = {"class":"paleblue"}


class DeliveriesTable(tables.Table):
  order = tables.LinkColumn('order_detail', args=[A('order.pk')])
  pk = CustomTextLinkColumn('delivery_detail', args=[A('pk')], custom_text="Detail", orderable=False, verbose_name="Actions")
  customer = tables.Column(accessor="order.customer", verbose_name="Customer")
  delivery_cost = DollarAmountColumn()

  class Meta:
    model = OrderDelivery
    attrs = {"class":"paleblue"}
    fields = ("order", "customer", "scheduled_delivery_date", "delivery_type", "delivery_cost", 'delivered_date') 

class SalesTotalsTable(tables.Table):
  item = tables.Column(verbose_name="-", orderable=False)
  hq = tables.Column(verbose_name="HQ/Sacramento", orderable=False)
  fnt = tables.Column(verbose_name="Roseville", orderable=False)
  total = tables.Column(verbose_name="Stores Total", orderable=False)

  class Meta:
    attrs = {"class":"paleblue"}

