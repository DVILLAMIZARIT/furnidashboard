# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Order.referral'
        db.add_column('order_info', 'referral',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Order.referral'
        db.delete_column('order_info', 'referral')


    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer', 'db_table': "'customers'"},
            'billing_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'shipping_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']"}),
            'subtotal_after_discount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        },
        u'orders.orderdelivery': {
            'Meta': {'object_name': 'OrderDelivery', 'db_table': "'deliveries'"},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'delivered_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_slip': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'delivery_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'pickup_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']"}),
            'scheduled_delivery_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'orders.orderitem': {
            'Meta': {'object_name': 'OrderItem', 'db_table': "'order_items'"},
            'ack_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'ack_num': ('django.db.models.fields.CharField', [], {'max_length': '125', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'eta': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_stock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'po_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'po_num': ('django.db.models.fields.CharField', [], {'max_length': '125', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'})
        },
        u'stores.store': {
            'Meta': {'object_name': 'Store', 'db_table': "'stores'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '125'})
        }
    }

    complete_apps = ['orders']