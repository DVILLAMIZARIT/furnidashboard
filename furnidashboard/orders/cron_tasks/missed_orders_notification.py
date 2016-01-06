from orders.models import Order
import orders.cron_tasks.utils as cron_utils
from stores.models import Store

def run_missed_orders_cron():
    msg = []
    report_is_blank = True

    orders_missing = __determine_potentially_missed_orders()    
    if orders_missing:
        report_is_blank = False
        msg.append("<strong>There are {0} potentially MISSING orders.</strong>".format(len(orders_missing)))

        items = []
        items.append("<table border=\"1\">")
        items.append("<thead><th>Order #</th></thead><tbody>")
        for o in orders_missing:
            items.append("<tr><td>{0}</td></tr>".format(str(o)))
        items.append("</tbody></table>")
        msg.append("".join(items))

        msg.append("<strong>***NOTE: please verify that your orders have been entered. If the POS order is a quote, select a status of 'Dummy' for order in FurniCloud.</strong>")
        msg.append("<br/>")

    msg.append("<strong>Please visits the 'Alerts' page on FurniCloud for full report</strong>".upper())

    # send email notifications
    if not report_is_blank:
      cron_utils.send_emails(message="<br/>".join(msg))

def __determine_potentially_missed_orders():
    res = []
#launch_dt = datetime(2014, 6, 1)
#if settings.USE_TZ:
#  launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())

#orders = Order.objects.filter(order_date__gte=launch_dt, number__istartswith="SO") 
    orders = Order.objects.get_qs().filter(number__istartswith="SO")

    sac_orders = orders.filter(store=Store.objects.get(name="Sacramento"))
    fnt_orders = orders.filter(store=Store.objects.get(name="Roseville"))

    sac_order_nums = sorted(map(lambda o: int(o.number[-4:]), sac_orders))
    fnt_order_nums = sorted(map(lambda o: int(o.number[-4:]), fnt_orders))

    lst = __find_skipped_order_nums(sac_order_nums, "SO-1")
    if lst:
      res += lst

    lst = __find_skipped_order_nums(fnt_order_nums, "SO-3")
    if lst:
      res += lst

    return res

def __find_skipped_order_nums(order_nums, prefix):

    res = []
    err_msg = "Order #{0}{1:04d}"

    if order_nums:
      first = order_nums[0]
      expected = first + 1
      for num in order_nums[1:]:
        if num != expected:
          res.append(err_msg.format(prefix, expected))
          expected = expected + 1
          while expected < num:
            res.append(err_msg.format(prefix, expected))
            expected = expected + 1
          if expected <= num:
            expected = expected + 1
        else:
          expected = num + 1

    return res
