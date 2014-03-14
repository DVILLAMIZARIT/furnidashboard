from django.db import models
from customers.models import Customer
from stores.models import Store
from django.core.urlresolvers import reverse

class Order(models.Model):
  """
  A model class representing Order data
  """
  ORDER_STATUSES = (
    ('SP', 'Special Order'),
    ('SO', 'Sold Order'),
    ('ST', 'Sold/Special Order'),
  )

  number = models.CharField(max_length=50)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  customer = models.ForeignKey(Customer, default=0, blank=True, null=True)
  status = models.CharField(max_length=5, choices=ORDER_STATUSES)
  deposit_balance = models.FloatField()
  subtotal_after_discount = models.FloatField()
  tax = models.FloatField()
  shipping = models.FloatField()
  comments = models.TextField()
  store = models.ForeignKey(Store)

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
  
  def __unicode__(self):
    return "{0}, {1}".format(self.number, self.grand_total)

  def get_absolute_url(self):
    return reverse("order_detail", kwargs={"pk":self.pk})
