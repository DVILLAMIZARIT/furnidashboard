from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order, OrderItem, OrderDelivery
from customers.models import Customer
from stores.models import Store
from commissions.models import Commission
from orders.utils import _calc_sales_assoc_by_orders

def create_sample_data():

    now  = datetime.now()
    this_m_first = datetime(now.year, now.month, 1)
    this_m_first = timezone.make_aware(this_m_first, timezone.get_current_timezone())

    last_m_mid = this_m_first - timedelta(days=16)

    last_m_first = datetime(last_m_mid.year, last_m_mid.month, 1)

    create_test_users()

    cust = Customer(first_name="TestCust1", last_name="L")
    cust.save()
    cust2 = Customer(first_name="TestCust2", last_name="L")
    cust2.save()
    cust3 = Customer(first_name="TestCust3", last_name="L")
    cust3.save()

    store1 = Store(name="Sacramento")
    store2 = Store(name="Roseville")
    store1.save()
    store2.save()

    users = User.objects.all()
    user1 = users.get(username="user1")
    user2 = users.get(username="user2")
    user3 = users.get(username="user3")
    user4 = users.get(username="user4")

    o = Order()
    o.number = 1
    o.order_date = this_m_first
    o.customer = cust
    o.status = 'N'
    o.deposit_balance = 100.00
    o.subtotal_after_discount = 3500.00 
    o.store = store1
    o.save()

    commission = Commission(associate=user1, order=o)
    commission.save()

    item1 = OrderItem(status='S', description="Item1", order=o)
    item1.save()

    o = Order()
    o.number = 2 
    o.order_date = last_m_mid
    o.customer = cust2
    o.status = 'Q'
    o.deposit_balance = 500
    o.subtotal_after_discount = 7000.00 
    o.store = store2
    o.save()

    commission = Commission(associate=user3, order=o)
    commission.save()
    commission = Commission(associate=user4, order=o)
    commission.save()

    item1 = OrderItem(status='P', description="Item2", order=o)
    item1.save()
    item2 = OrderItem(status='S', description="Item3", order=o)
    item2.save()

    o = Order()
    o.number = 3 
    o.order_date = last_m_first
    o.customer = cus3t
    o.status = 'C'
    o.deposit_balance = 5000
    o.subtotal_after_discount = 5000.00 
    o.store = store1
    o.save()

    commission = Commission(associate=user3, order=o)
    commission.save()
    commission = Commission(associate=user4, order=o)
    commission.save()

    item1 = OrderItem(status='P', description="Item4", order=o)
    item1.save()
    item2 = OrderItem(status='S', description="Item6", order=o)
    item2.save()
    item2 = OrderItem(status='O', description="Item7", order=o)
    item2.save()

def create_test_users():
    content_type = ContentType.objects.get_for_model(Order)
    perm = Permission.objects.get(content_type=content_type, codename="view_orders")
    privileged_group = Group.objects.create(name="privileged")
    privileged_group.permissions.add(perm)
    privileged_group.save()
   
    delivery_persons_group = Group.objects.create(name="delivery_persons")
    content_type = ContentType.objects.get_for_model(OrderDelivery)
    perm = Permission.objects.get(content_type=content_type, codename="change_orderdelivery")
    delivery_persons_group.permissions.add(perm)
    delivery_persons_group.save()
    
    manager_usr = User.objects.create(username="user1", email="test@gmail.com", is_active=1, is_staff=1, first_name="User1", last_name="L")
    manager_usr.set_password("secret")
    manager_usr.groups.add(privileged_group)
    manager_usr.save()

    delivery_usr = User.objects.create(username="user2", email="test2@gmail.com", is_active=1, is_staff=1, first_name="User2", last_name="L")
    delivery_usr.set_password("secret")
    delivery_usr.groups.add(delivery_persons_group)
    delivery_usr.save()

    user3 = User.objects.create(username="user3", email="test3@gmail.com", is_active=1, is_staff=1, first_name="User3", last_name="L")
    user3.set_password("secret")
    user3.groups.add(privileged_group)
    user3.save()

    user4 = User.objects.create(username="user4", email="test4@gmail.com", is_active=1, is_staff=1, first_name="User4", last_name="L")
    user4.set_password("secret")
    user4.groups.add(privileged_group)
    user4.save()

def create_customers():
  pass
