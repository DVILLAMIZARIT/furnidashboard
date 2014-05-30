from django.conf import settings
from orders.models import Order

def _calc_sales_assoc_by_orders(order_list, include_bonus=True):
  res = {}
  # month_start = datetime(int(year), int(month), 1)
  # month_end = month_start + timedelta(35)
  # month_end = datetime(month_end.year, month_end.month, 1)
  # orders = Order.objects.filter(Q(created__gte=month_start) & Q(created__lt=month_end))
  
  for o in order_list:
    split_num = o.commission_set.count()
    comm_queryset = o.commission_set.select_related().all() 
    for com in comm_queryset:
      sales_amount = o.subtotal_after_discount / split_num
      comm_amount = sales_amount * settings.COMMISSION_PERCENT
      commissions_paid = comm_amount if com.paid else 0.0                            #paid commissions amount
      commissions_pending = 0.0
      commissions_due = 0.0

      if not com.paid:
        #commission is pending if order status is not Dummy, Delivered, or Closed
        commissions_pending = comm_amount if o.status not in ('D', 'X', 'C') else 0.0   

        #otherwise, if order is Delivered, or Closed, commission is due
        commissions_due = comm_amount if o.status in ('D', 'C') else 0.0

      temp_subtotal = {'sale': sales_amount, 
          'commissions_pending': commissions_pending, 
          'commissions_due': commissions_due, 
          'commissions_paid': commissions_paid}

      if res.has_key(com.associate.first_name):
        res[com.associate.first_name]['sale'] += temp_subtotal['sale'] 
        res[com.associate.first_name]['commissions_pending'] += temp_subtotal['commissions_pending'] 
        res[com.associate.first_name]['commissions_due'] += temp_subtotal['commissions_due'] 
        res[com.associate.first_name]['commissions_paid'] += temp_subtotal['commissions_paid'] 
      else:
        res[com.associate.first_name] =  temp_subtotal
  
  sales_list = []
  for associate, temp_subtotal in res.items():
    bonus = _calc_bonus_amount(temp_subtotal['sale'])
    sales_list.append({'associate':associate, 
      'sales':'{0:.2f}'.format(temp_subtotal['sale']), 
      'commissions_due':'{0:.2f}'.format(temp_subtotal['commissions_due']), 
      'commissions_paid':'{0:.2f}'.format(temp_subtotal['commissions_paid']),
      'commissions_pending':'{0:.2f}'.format(temp_subtotal['commissions_pending']),
      'bonus':bonus})

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

