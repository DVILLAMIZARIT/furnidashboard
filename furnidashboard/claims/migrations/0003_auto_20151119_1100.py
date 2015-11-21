# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0002_auto_20151105_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorClaimRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'claims/%Y/%m')),
                ('data_fields', models.TextField(default=b'', blank=True)),
            ],
            options={
                'db_table': 'claim_vendor_requests',
            },
        ),
        migrations.AlterField(
            model_name='claim',
            name='claim_desc',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='order_invoice_num',
            field=models.CharField(default=b'', max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='paid_by',
            field=models.CharField(default=b'', max_length=128, blank=True, choices=[(b'VND', b'Vendor'), (b'FURN', b'Furnitalia'), (b'CUST', b'Customer')]),
        ),
        migrations.AlterField(
            model_name='claim',
            name='repair_tech',
            field=models.CharField(default=b'', max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='vendor_claim_no',
            field=models.CharField(default=b'', max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='claimphoto',
            name='description',
            field=models.CharField(default=b'', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='claimphoto',
            name='file',
            field=models.FileField(upload_to=b'claims/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='claimstatus',
            name='status_desc',
            field=models.CharField(default=b'', max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='vendorclaimrequest',
            name='claim',
            field=models.ForeignKey(to='claims.Claim'),
        ),
    ]
