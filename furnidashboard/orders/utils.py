from orders.models import Order

def _calc_sales_assoc_by_orders(order_list):
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
    sales_list.append({'associate':associate, 'sales':amount})

  return sales_list

