from django.db import models
from django.db.models import Q
from customers.models import Customer
from stores.models import Store
from django.core.urlresolvers import reverse

class OrderManager(models.Manager):
  def unplaced_orders(self):
    return super(OrderManager, self).get_query_set().filter((Q(status=None) | Q(status='N') | (Q(orderitem__in_stock=False) & (Q(orderitem__in_stock=False) & (Q(orderitem__po_num__isnull=True) | Q(orderitem__po_num="")))))).distinct()

class Order(models.Model):
  """
  A model class representing Order data
  """
  ORDER_STATUSES = (
    ('N', 'New'),
    ('C', 'Closed'),
    ('H', 'On Hold'),
    ('P', 'In Production'),
    ('T', 'In Transit'),
    ('S', 'Scheduled for Delivery'),
    ('D', 'Delivered'),
  )

  number = models.CharField(max_length=50)
  created = models.DateTimeField() # auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  customer = models.ForeignKey(Customer, default=0, blank=True, null=True)
  status = models.CharField(max_length=5, choices=ORDER_STATUSES)
  deposit_balance = models.FloatField(blank=True, default=0.0)
  subtotal_after_discount = models.FloatField(blank=True, default=0.0)
  tax = models.FloatField(blank=True, default=0.0)
  shipping = models.FloatField(blank=True, default=0.0)
  comments = models.TextField(blank=True)
  store = models.ForeignKey(Store)
  referral = models.CharField(blank=True, null=True, max_length=50)
  
  #objects = models.Manager()      #default
  objects = OrderManager() #customer manager

  @property
  def not_placed(self):
           # no status        'new'                 'any item, which is not in stock, and does not have po#
    return not self.status or self.status == 'N' or any([item for item in self.orderitem_set if not item.in_stock and not item.po_num])

  @property
  def balance_due(self):
    "Balance due after the deposits"
    return self.grand_total - self.deposit_balance

  @property
  def grand_total(self):
    "Grand Total (Subtotal + tax + shipping)"
    return self.subtotal_after_discount + self.tax + self.shipping

  class Meta:
    ordering = ["-created","-modified"]
    db_table = "order_info"
    permissions = (
        ("view_orders", "Can View Orders"),
        ("view_sales", "Can View Sales Reports"),
    )
  
  def __unicode__(self):
    return "{0}, {1}".format(self.number, self.grand_total)

  def get_absolute_url(self):
    return reverse("order_detail", kwargs={"pk":self.pk})

class OrderItem(models.Model):
  """
  A model class representing Items Ordered (stock items, special order items, etc).
  """
  ITEM_STATUSES = (
    ('P', 'Pending'),
    ('O', 'Ordered'),
    ('R', 'Received'),
    ('D', 'Delivered'),
  )

  order = models.ForeignKey(Order)
  status = models.CharField(max_length=15, choices=ITEM_STATUSES, blank=True, null=True)
  in_stock = models.BooleanField(default=True, blank=True)
  description = models.CharField(max_length=255)
  po_num = models.CharField(max_length=125, blank=True)
  po_date = models.DateField(blank=True, null=True)
  ack_num = models.CharField(max_length=125, blank=True)
  ack_date = models.DateField(blank=True, null=True)
  eta = models.DateField(blank=True, null=True)

  class Meta:
    db_table = "order_items"
    verbose_name_plural = "ordered items"
  
class OrderDelivery(models.Model):
  """
  A model class representing deliveries  tracking for Orders 
  """

  DELIVERY_TYPES = (
      ('SELF', 'Self Pickup'),
      ('RFD', 'Roberts Furniture Delivery'),
      ('MGL', 'Miguel'),
      ('CUSTOM', 'Other'),
  )

  order = models.ForeignKey(Order)
  delivery_type =  models.CharField(max_length=25, choices=DELIVERY_TYPES, blank=True, null=True)
  scheduled_delivery_date = models.DateField(null=True, blank=True)
  delivered_date = models.DateField(null=True, blank=True)
  pickup_from = models.ForeignKey(Store)
  delivery_slip = models.FileField(upload_to='deliveries/%Y/%m', blank=True, null=True)
  comments = models.TextField(blank=True, null=True)

  def get_absolute_url(self):
    return reverse("delivery_detail", kwargs={"pk":self.pk})

  @property
  def delivery_slip_filename(self):
    import os
    return os.path.basename(self.delivery_slip.name)

  class Meta:
    db_table = "deliveries"
    verbose_name_plural = "deliveries"

