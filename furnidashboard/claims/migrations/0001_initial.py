# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import audit_log.models.fields
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_with_session_key', audit_log.models.fields.CreatingSessionKeyField(max_length=40, null=True, editable=False)),
                ('modified_with_session_key', audit_log.models.fields.LastSessionKeyField(max_length=40, null=True, editable=False)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('claim_date', models.DateTimeField()),
                ('claim_desc', models.CharField(max_length=250, null=True, blank=True)),
                ('delivery_date', models.DateField(null=True, blank=True)),
                ('item_origin', models.CharField(max_length=128, choices=[(b'NTZ', b'Natuzzi Italia'), (b'EDITIONS', b'Natuzzi Editions'), (b'REVIVE', b'Natuzzi Re-Vive')])),
                ('vendor_claim_no', models.CharField(max_length=128, null=True, blank=True)),
                ('order_invoice_num', models.CharField(max_length=250, null=True, blank=True)),
                ('amount', models.FloatField(default=0.0, blank=True)),
                ('paid_by', models.CharField(blank=True, max_length=128, null=True, choices=[(b'NTZ', b'Natuzzi'), (b'FURN', b'Furnitalia'), (b'CUST', b'Customer')])),
                ('repair_tech', models.CharField(max_length=128, null=True, blank=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='created_claims_claim_set', editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='created by')),
                ('customer', models.ForeignKey(default=None, blank=True, to='customers.Customer', null=True)),
                ('modified_by', audit_log.models.fields.LastUserField(related_name='modified_claims_claim_set', editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='modified by')),
                ('order_ref', models.ForeignKey(default=None, blank=True, to='orders.Order', null=True)),
            ],
            options={
                'db_table': 'claims',
                'permissions': (('view_claims', 'Can View Claims'), ('edit_claims', 'Can Edit Claims')),
            },
        ),
        migrations.CreateModel(
            name='ClaimPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'attachments/%Y/%m')),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('claim', models.ForeignKey(to='claims.Claim')),
            ],
            options={
                'db_table': 'claim_photos',
            },
        ),
        migrations.CreateModel(
            name='ClaimStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_with_session_key', audit_log.models.fields.CreatingSessionKeyField(max_length=40, null=True, editable=False)),
                ('modified_with_session_key', audit_log.models.fields.LastSessionKeyField(max_length=40, null=True, editable=False)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('status', models.CharField(max_length=128, choices=[(b'NEW', b'New'), (b'SUBMITTED', b'Submitted'), (b'AUTHORIZED', b'Authorized'), (b'FUNDED', b'Funded'), (b'RECEIVED', b'Received'), (b'CANCELLED', b'Cancelled')])),
                ('date', models.DateTimeField()),
                ('status_desc', models.CharField(max_length=250, null=True, blank=True)),
                ('claim', models.ForeignKey(to='claims.Claim')),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='created_claims_claimstatus_set', editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='created by')),
                ('modified_by', audit_log.models.fields.LastUserField(related_name='modified_claims_claimstatus_set', editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='modified by')),
            ],
            options={
                'db_table': 'claim_status',
            },
        ),
    ]
