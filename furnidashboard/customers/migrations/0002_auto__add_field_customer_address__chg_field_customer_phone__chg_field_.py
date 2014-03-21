# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Customer.address'
        db.add_column('customers', 'address',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'Customer.phone'
        db.alter_column('customers', 'phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True))

        # Changing field 'Customer.email'
        db.alter_column('customers', 'email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True))

    def backwards(self, orm):
        # Deleting field 'Customer.address'
        db.delete_column('customers', 'address')


        # Changing field 'Customer.phone'
        db.alter_column('customers', 'phone', self.gf('django.db.models.fields.CharField')(default='', max_length=30))

        # Changing field 'Customer.email'
        db.alter_column('customers', 'email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75))

    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer', 'db_table': "'customers'"},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['customers']