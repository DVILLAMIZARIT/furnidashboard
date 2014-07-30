from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.conf import settings
import datetime
from orders.models import Order, OrderItem
from customers.models import Customer
from stores.models import Store
from commissions.models import Commission
import orders.utils as order_utils
from orders.sample_data import create_sample_data

class TestOrdersView(TestCase):
  def setUp(self):
    self.client = Client()

    create_sample_data()

    now  = datetime.datetime.now()
    self.this_m_first = datetime.datetime(now.year, now.month, 1)
    self.this_m_first = timezone.make_aware(self.this_m_first, timezone.get_current_timezone())

  def test_login_required(self):
    resp = self.client.get("/orders/")
    self.assertEqual(resp.status_code, 302)

    login_status = self.client.login(username="user1", password="secret")
    self.assertTrue(login_status)

    resp = self.client.get("/orders/")
    self.assertEqual(resp.status_code, 200)

  def test_commission(self):
    # simple order, 'new', 1 stock item, 1 associate
    o = Order.objects.get(number=1)
    self.assertNotEqual(o, None)

    comm_data = order_utils._calc_sales_assoc_by_orders([o], False)
    self.assertEqual(len(comm_data), 1)
    self.assertEqual(comm_data[0]['associate'], o.commission_set.all()[0].associate.first_name)
    self.assertEqual(float(comm_data[0]['commissions_due']), 0)
    self.assertEqual(float(comm_data[0]['commissions_pending']), o.subtotal_after_discount * settings.COMMISSION_PERCENT)

    comm_data = order_utils.calc_commissions_for_order(o)
    self.assertEqual(len(comm_data), 1)
    self.assertEqual(comm_data[0]['associate'], o.commission_set.all()[0].associate.first_name)
    self.assertEqual(float(comm_data[0]['commissions_due']), 0)
    self.assertEqual(float(comm_data[0]['commissions_pending']), o.subtotal_after_discount * settings.COMMISSION_PERCENT)

    # complex order -- pending, with 2 items: 1 stock, 1 pending, 2 associates
    o = Order.objects.get(number=2)
    self.assertNotEqual(o, None)
    order_associates = [c.associate.first_name for c in o.commission_set.all()]

    comm_data = order_utils._calc_sales_assoc_by_orders([o], False)
    self.assertEqual(len(comm_data), 2)
    self.assertTrue(all([com['associate'] in order_associates for com in comm_data])) 
    self.assertEqual(float(comm_data[0]['commissions_due']), 0)
    self.assertEqual(float(comm_data[0]['commissions_pending']), o.subtotal_after_discount / 2.00 * settings.COMMISSION_PERCENT)

    comm_data = order_utils.calc_commissions_for_order(o)
    self.assertEqual(len(comm_data), 2)
    self.assertTrue(all([com['associate'] in order_associates for com in comm_data])) 
    self.assertEqual(float(comm_data[0]['commissions_due']), 0)
    self.assertEqual(float(comm_data[1]['commissions_due']), 0)
    self.assertEqual(float(comm_data[1]['commissions_pending']), o.subtotal_after_discount / 2.00 * settings.COMMISSION_PERCENT)

  def tearDown(self):
    pass
