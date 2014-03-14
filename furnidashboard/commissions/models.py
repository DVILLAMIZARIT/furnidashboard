from django.db import models
from django.conf import settings
from orders.models import Order

class Commission(models.Model):
  associate = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, blank=True, null=True)
  order = models.OneToOneField(Order)
  claimed = models.BooleanField(default=False, blank=True)
  claimed_date = models.DateField(null=True, blank=True)
  paid = models.BooleanField(default=False, blank=True)
  paid_date = models.DateField(null=True, blank=True)

  class Meta:
    db_table = "commissions"
