# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Commission.created_by'
        db.add_column('commissions', 'created_by',
                      self.gf('audit_log.models.fields.CreatingUserField')(related_name='created_commission_set', to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Commission.created_with_session_key'
        db.add_column('commissions', 'created_with_session_key',
                      self.gf('audit_log.models.fields.CreatingSessionKeyField')(max_length=40, null=True),
                      keep_default=False)

        # Adding field 'Commission.modified_by'
        db.add_column('commissions', 'modified_by',
                      self.gf('audit_log.models.fields.LastUserField')(related_name='modified_commission_set', to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Commission.modified_with_session_key'
        db.add_column('commissions', 'modified_with_session_key',
                      self.gf('audit_log.models.fields.LastSessionKeyField')(max_length=40, null=True),
                      keep_default=False)

        # Adding field 'Commission.created'
        db.add_column('commissions', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True),
                      keep_default=False)

        # Adding field 'Commission.modified'
        db.add_column('commissions', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Commission.created_by'
        db.delete_column('commissions', 'created_by_id')

        # Deleting field 'Commission.created_with_session_key'
        db.delete_column('commissions', 'created_with_session_key')

        # Deleting field 'Commission.modified_by'
        db.delete_column('commissions', 'modified_by_id')

        # Deleting field 'Commission.modified_with_session_key'
        db.delete_column('commissions', 'modified_with_session_key')

        # Deleting field 'Commission.created'
        db.delete_column('commissions', 'created')

        # Deleting field 'Commission.modified'
        db.delete_column('commissions', 'modified')


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
        u'commissions.commission': {
            'Meta': {'object_name': 'Commission', 'db_table': "'commissions'"},
            'associate': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['auth.User']", 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'created_commission_set'", 'to': u"orm['auth.User']"}),
            'created_with_session_key': ('audit_log.models.fields.CreatingSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'modified_commission_set'", 'to': u"orm['auth.User']"}),
            'modified_with_session_key': ('audit_log.models.fields.LastSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
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
        u'orders.order': {
            'Meta': {'ordering': "['-created', '-modified']", 'object_name': 'Order', 'db_table': "'order_info'"},
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
            'number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stores.Store']"}),
            'subtotal_after_discount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        },
        u'stores.store': {
            'Meta': {'object_name': 'Store', 'db_table': "'stores'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '125'})
        }
    }

    complete_apps = ['commissions']