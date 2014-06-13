from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from audit_log.models import AuthStampedModel
from django_extensions.db.models import TimeStampedModel
from customers.models import Customer
from stores.models import Store

class OrderManager(models.Manager):
  #launch_dt = datetime(2014, 6, 1)
  launch_dt = datetime(2014, 5, 1)
  if settings.USE_TZ:
    launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())

  def get_qs(self):
    qs = super(OrderManager, self).get_query_set().filter(order_date__gte=self.launch_dt)
    return qs
  
  def unplaced_orders(self):
    #special order, not placed (no PO number)
    qs = self.get_qs()
    return qs.filter(Q(status='N') | (Q(orderitem__in_stock=False) & Q(orderitem__po_num=""))).distinct()

  def open_orders(self):
    return self.get_qs().filter(~Q(status='C'))
    
  def ordered_not_acknowledged(self):
    #special order has been placed, but no acknowledgement number
    qs = self.get_qs()
    return qs.filter(~Q(orderitem__po_num="") & Q(orderitem__ack_num="")).distinct()
  
  def special_acknowledged_no_eta(self):
    #special order has been placed and acknowledged, but no ETA
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['O', 'P']) & ~Q(orderitem__ack_num="") & Q(orderitem__eta__isnull=True)).distinct()
  
  def special_eta_passed_not_received(self):
    #special order ETA has passed, but item status is not 'Received'
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['O', 'P']) & Q(orderitem__eta__gte=datetime.now())).distinct()
  
  def not_yet_delivered(self):
    #undelivered orders
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['S', 'R']))

  def commissions_unpaid(self):
    # orders with unpaid commissions
    qs = self.get_qs()
    return qs.filter(Q(status__in=['D', 'C']) & Q(commission__paid=False))
  
class Order(TimeStampedModel, AuthStampedModel):
  """
  A model class representing Order data
  """
  ORDER_STATUSES = (
    ('N', 'New'),
    ('Q', 'Pending'),
    ('H', 'On Hold'),
    ('P', 'In Production'),
    ('T', 'In Transit'),
    ('S', 'Scheduled for Delivery'),
    ('D', 'Delivered'),
    ('X', 'Dummy'),
    ('C', 'Closed'),
  )

  REFERRAL_SOURCES = (
    ('NO', 'Not Referred'),
    ('REF', 'Referred by friends/relatives/acquintance'),
    ('WEB', 'Website'),
    ('MAG', 'Magazine'),
    ('SOC', 'Social networks'),
    ('NWP', 'Newspaper'),
    ('TV', 'TV'),
  )

  number = models.CharField(max_length=50, unique=True)
  order_date = models.DateTimeField(null=True)
  customer = models.ForeignKey(Customer, default=0, blank=True, null=True)
  status = models.CharField(max_length=5, choices=ORDER_STATUSES)
  deposit_balance = models.FloatField(blank=True, default=0.0)
  subtotal_after_discount = models.FloatField(blank=True, default=0.0)
  tax = models.FloatField(blank=True, default=0.0)
  shipping = models.FloatField(blank=True, default=0.0)
  comments = models.TextField(blank=True)
  store = models.ForeignKey(Store)
  referral = models.CharField(blank=True, null=True, max_length=50, choices=REFERRAL_SOURCES)
  
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
    ordering = ["-order_date"]
    db_table = "order_info"
    permissions = (
        ("view_orders", "Can View Orders"),
        ("view_sales", "Can View Sales Reports"),
        ("update_status", "Can Update Order Status"),
    )
  
  def __unicode__(self):
    return "{0}, {1}".format(self.number, self.grand_total)

  def get_absolute_url(self):
    return reverse("order_detail", kwargs={"pk":self.pk})

#class OrderItem(models.Model):
class OrderItem(TimeStampedModel, AuthStampedModel):
  """
  A model class representing Items Ordered (stock items, special order items, etc).
  """
  ITEM_STATUSES = (
    ('P', 'Pending'),
    ('O', 'Ordered'),
    ('R', 'Received'),
    ('D', 'Delivered'),
    ('S', 'In Stock'),
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
  
class OrderDelivery(TimeStampedModel, AuthStampedModel):
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
  pickup_from = models.ForeignKey(Store, blank=True, null=True)
  delivery_slip = models.FileField(upload_to='deliveries/%Y/%m', blank=True, null=True)
  comments = models.TextField(blank=True, null=True)
  delivery_person_notes = models.TextField(blank=True, null=True)
  delivery_cost = models.FloatField(blank=True, default=0.0)
  paid = models.BooleanField(default=False, blank=True)

  def get_absolute_url(self):
    return reverse("delivery_detail", kwargs={"pk":self.pk})

  @property
  def delivery_slip_filename(self):
    import os
    return os.path.basename(self.delivery_slip.name)

  class Meta:
    db_table = "deliveries"
    verbose_name_plural = "deliveries"
    permissions = (
      ("modify_delivery_fee", "Modify Delivery Fee"),
    )
