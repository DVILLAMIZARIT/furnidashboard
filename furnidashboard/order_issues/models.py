from django.db import models
from django_extensions.db.models import TimeStampedModel
from audit_log.models import AuthStampedModel
from orders.models import Order

class OrderIssue(TimeStampedModel, AuthStampedModel):
  ISSUE_STATUSES =  (
    ('N', 'New'),
    ('C', 'Claim submitted'),
    ('T', 'Technician sent'),
    ('E', 'Eligible for Credit'),
    ('R', 'Resolved'),
  )

  order = models.ForeignKey(Order)
  status = models.CharField(max_length=5, choices=ISSUE_STATUSES)
  comments = models.TextField(blank=True, null=True)

  class Meta:
    db_table = "order_issues"
    permissions = (
      ("update_order_issues", "Can Update Order Issues (Claims)Information"),
    )
