# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Order.vendor_order_no'
        db.add_column('order_info', 'vendor_order_no',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Order.vendor_placed_order_date'
        db.add_column('order_info', 'vendor_placed_order_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Order.vendor_order_no'
        db.delete_column('order_info', 'vendor_order_no')

        # Deleting field 'Order.vendor_placed_order_date'
        db.delete_column('order_info', 'vendor_placed_order_date')


    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer', 'db_table': "'customers'"},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'orders.order': {
            'Meta': {'ordering': "['-created', '-modified']", 'object_name': 'Order', 'db_table': "'order_info'"},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['customers.Customer']", 'null': 'True', 'blank': 'True'}),
            'deposit_balance': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']"}),
            'subtotal_after_discount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'vendor_order_no': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'vendor_placed_order_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'stores.store': {
            'Meta': {'object_name': 'Store', 'db_table': "'stores'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '125'})
        }
    }

    complete_apps = ['orders']