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
      commission_amount = o.subtotal_after_discount / split_num
      if res.has_key(com.associate.first_name):
        res[com.associate.first_name] += commission_amount 
      else:
        res[com.associate.first_name] =  commission_amount
  
  sales_list = []
  for associate, amount in res.items():
    bonus = _calc_bonus_amount(amount)
    sales_list.append({'associate':associate, 'sales':amount, 'bonus':bonus})

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

