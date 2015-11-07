# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='claim',
            options={'ordering': ['-claim_date'], 'permissions': (('view_claims', 'Can View Claims'), ('edit_claims', 'Can Edit Claims'))},
        ),
        migrations.AlterModelOptions(
            name='claimstatus',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='claim',
            name='claim_desc',
            field=models.TextField(null=True, blank=True),
        ),
    ]
