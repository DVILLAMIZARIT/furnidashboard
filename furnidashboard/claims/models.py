from django.db import models
from django.core.urlresolvers import reverse
from django_extensions.db.models import TimeStampedModel
from django.utils import formats
from audit_log.models import AuthStampedModel
from orders.models import Order, OrderItem
from customers.models import Customer


class Claim(TimeStampedModel, AuthStampedModel):
    """
    A model class representing the Claim information for sold orders/items
    """

    PAID_BY_CHOICES = (
        ('NTZ', 'Natuzzi'),
        ('FURN', 'Furnitalia'),
        ('CUST', 'Customer'),
    )

    CLAIM_VENDORS = (
        ('NTZ', 'Natuzzi Italia'),
        ('EDITIONS', 'Natuzzi Editions'),
        ('REVIVE', "Natuzzi Re-Vive"),
    )

    claim_date = models.DateTimeField(null=False)
    claim_desc = models.TextField(blank=True, null=True)
    delivery_date = models.DateField(null=True, blank=True)
    item_origin = models.CharField(null=False, blank=False, choices=CLAIM_VENDORS, max_length=128)
    vendor_claim_no = models.CharField(null=True, blank=True, max_length=128)
    customer = models.ForeignKey(Customer, default=None, blank=True, null=True)
    order_ref = models.ForeignKey(Order, default=None, blank=True, null=True)
    order_invoice_num = models.CharField(null=True, blank=True, max_length=250)
    amount = models.FloatField(blank=True, default=0.0)
    paid_by = models.CharField(null=True, blank=True, choices=PAID_BY_CHOICES, max_length=128)
    repair_tech = models.CharField(null=True, blank=True, max_length=128)

    def __unicode__(self):
        return "Claim: #%s, date:%s, customer:%s" % (
            self.pk, formats.date_format(self.claim_date, 'DATE_FORMAT_SHORT'), str(self.customer))

    def get_absolute_url(self):
        return reverse("claim_detail", kwargs={"pk": self.pk})

    class Meta:
        db_table = "claims"
        ordering = ["-claim_date"]
        permissions = (
            ("view_claims", "Can View Claims"),
            ("edit_claims", "Can Edit Claims"),
        )


class ClaimStatus(TimeStampedModel, AuthStampedModel):
    """
    A model class representing the Statuses for a claim 
    """
    CLAIM_STATUSES = (
        ('NEW', 'New'),
        ('SUBMITTED', 'Submitted'),
        ('AUTHORIZED', 'Authorized'),
        ('FUNDED', 'Funded'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    )

    claim = models.ForeignKey(Claim)
    status = models.CharField(null=False, blank=False, choices=CLAIM_STATUSES, max_length=128)
    date = models.DateTimeField(null=False, blank=False)
    status_desc = models.CharField(null=True, blank=True, max_length=250)

    def __unicode__(self):
        return "Claim Status: %s, date=%s, claim #%s" % (
            self.get_status_display(), formats.date_format(self.date, 'j F, Y'), self.claim.pk)

    class Meta:
        db_table = "claim_status"
        ordering = ["-date"]


class ClaimPhoto(models.Model):
    """
    A model class for storing Claim photos
    """

    claim = models.ForeignKey(Claim)
    file = models.FileField(upload_to='claims/%Y/%m')
    description = models.CharField(max_length=255, blank=True, null=True)

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)

    def __unicode__(self):
        if len(self.description):
            return self.description
        else:
            return ""

    class Meta:
        db_table = "claim_photos"
