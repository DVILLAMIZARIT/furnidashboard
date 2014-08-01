# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Attachment'
        db.create_table(u'orders_attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'orders', ['Attachment'])

        # Adding model 'DeliveryAttachment'
        db.create_table('delivery_attachments', (
            (u'attachment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['orders.Attachment'], unique=True, primary_key=True)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.OrderDelivery'])),
        ))
        db.send_create_signal(u'orders', ['DeliveryAttachment'])

        # Adding model 'OrderAttachment'
        db.create_table('order_attachments', (
            (u'attachment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['orders.Attachment'], unique=True, primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Order'])),
        ))
        db.send_create_signal(u'orders', ['OrderAttachment'])

        # Adding unique constraint on 'Order', fields ['number']
        db.create_unique('order_info', ['number'])


    def backwards(self, orm):
        # Removing unique constraint on 'Order', fields ['number']
        db.delete_unique('order_info', ['number'])

        # Deleting model 'Attachment'
        db.delete_table(u'orders_attachment')

        # Deleting model 'DeliveryAttachment'
        db.delete_table('delivery_attachments')

        # Deleting model 'OrderAttachment'
        db.delete_table('order_attachments')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        u'orders.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'orders.deliveryattachment': {
            'Meta': {'object_name': 'DeliveryAttachment', 'db_table': "'delivery_attachments'", '_ormbases': [u'orders.Attachment']},
            u'attachment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['orders.Attachment']", 'unique': 'True', 'primary_key': 'True'}),
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.OrderDelivery']"})
        },
        u'orders.order': {
            'Meta': {'ordering': "['-order_date']", 'object_name': 'Order', 'db_table': "'order_info'"},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'created_order_set'", 'to': u"orm['auth.User']"}),
            'created_with_session_key': ('audit_log.models.fields.CreatingSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['customers.Customer']", 'null': 'True', 'blank': 'True'}),
            'deposit_balance': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'modified_order_set'", 'to': u"orm['auth.User']"}),
            'modified_with_session_key': ('audit_log.models.fields.LastSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'order_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']"}),
            'subtotal_after_discount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        },
        u'orders.orderattachment': {
            'Meta': {'object_name': 'OrderAttachment', 'db_table': "'order_attachments'", '_ormbases': [u'orders.Attachment']},
            u'attachment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['orders.Attachment']", 'unique': 'True', 'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"})
        },
        u'orders.orderdelivery': {
            'Meta': {'object_name': 'OrderDelivery', 'db_table': "'deliveries'"},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'created_orderdelivery_set'", 'to': u"orm['auth.User']"}),
            'created_with_session_key': ('audit_log.models.fields.CreatingSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'delivered_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'delivery_person_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_slip': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'delivery_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'modified_orderdelivery_set'", 'to': u"orm['auth.User']"}),
            'modified_with_session_key': ('audit_log.models.fields.LastSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pickup_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']", 'null': 'True', 'blank': 'True'}),
            'scheduled_delivery_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'orders.orderitem': {
            'Meta': {'object_name': 'OrderItem', 'db_table': "'order_items'"},
            'ack_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'ack_num': ('django.db.models.fields.CharField', [], {'max_length': '125', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'created_orderitem_set'", 'to': u"orm['auth.User']"}),
            'created_with_session_key': ('audit_log.models.fields.CreatingSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'eta': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_stock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'modified_orderitem_set'", 'to': u"orm['auth.User']"}),
            'modified_with_session_key': ('audit_log.models.fields.LastSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
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