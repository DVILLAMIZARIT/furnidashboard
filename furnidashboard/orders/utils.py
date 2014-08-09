from django.conf import settings
from orders.models import Order
import re

def calc_commissions_for_order(order):
  # returns the list containing key-value commissions data
  # per associate
  
  coms = []

  associates_cnt = order.commission_set.count()
  comm_queryset = order.commission_set.select_related().all() 
  for com in comm_queryset:
    sales_amount = order.subtotal_after_discount / float(associates_cnt)
    comm_amount = sales_amount * settings.COMMISSION_PERCENT

    if com.paid:
      amount_paid = comm_amount
      amount_pending = 0.0
      amount_due = 0.0
    else :
      amount_paid = 0.0
      #commission is pending if order status is not Dummy, Delivered, or Closed
      amount_pending = comm_amount if order.status not in ('D', 'X', 'C') else 0.0 
      #otherwise, if order is Delivered, or Closed, commission is due
      amount_due= comm_amount if order.status in ('D', 'C') else 0.0

    temp_subtotal = {
        'associate': com.associate.first_name,
        'sale': sales_amount, 
        'commissions_pending': amount_pending, 
        'commissions_due': amount_due, 
        'commissions_paid': amount_paid
    }

    coms.append(temp_subtotal)
  
  return coms


def _calc_sales_assoc_by_orders(order_list, include_bonus=True):
  # returns a list of commissions data stored as key-val pair

  res = {}
  
  for o in order_list:
    order_coms = calc_commissions_for_order(o)
    for com in order_coms:

      if res.has_key(com['associate']):
        res[com['associate']]['sale'] += com['sale'] 
        res[com['associate']]['commissions_pending'] += com['commissions_pending'] 
        res[com['associate']]['commissions_due'] += com['commissions_due'] 
        res[com['associate']]['commissions_paid'] += com['commissions_paid'] 
      else:
        res[com['associate']] =  com
  
  sales_list = []
  for associate, temp_subtotal in res.items():
    bonus = _calc_bonus_amount(temp_subtotal['sale'])
    sales_list.append({
      'associate':          associate, 
      'sales':              temp_subtotal['sale'], 
      'commissions_due':    temp_subtotal['commissions_due'], 
      'commissions_paid':   temp_subtotal['commissions_paid'],
      'commissions_pending':temp_subtotal['commissions_pending'],
      'bonus':              bonus
    })

  return sales_list

def _calc_bonus_amount(sales_amount):
  bonus = 0.0
  
  if 25000.0 <= sales_amount < 35000.0:
    bonus = 50.0 
  elif 35000.0 <= sales_amount < 45000.0:
    bonus = 100.0
  elif 45000.0 <= sales_amount < 50000.0:
    bonus = 150.0
  elif 50000.0 <= sales_amount < 60000.0:
    bonus = 200.0
  elif 60000.0 <= sales_amount < 75000.0:
    bonus = 250.0
  elif sales_amount >= 75000.0:
    bonus = 300.0

  return bonus

def is_valid_order_number(number):
  return re.match(settings.ORDER_FORMAT_REGEX, number) != None

def is_duplicate_order_exists(number, instance):
  try:
    o = Order.objects.get(number__iexact=number)

    if instance != None and instance.pk and o.pk == instance.pk:
      return False
    
    return True

  except Exception :
    return False
