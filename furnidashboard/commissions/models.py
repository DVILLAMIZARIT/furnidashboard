from django.db import models
from django.conf import settings
from orders.models import Order

class Commission(models.Model):
  associate = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, null=False, blank=True)
  order = models.ForeignKey(Order)
  paid = models.BooleanField(default=False, blank=True)
  paid_date = models.DateField(null=True, blank=True)

  class Meta:
    db_table = "commissions"
    permissions = (
      ("update_commissions_payment", "Can Update Commission Payment Information"),
    )
