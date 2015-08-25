from orders.models import Order
import orders.utils as order_utils
import orders.cron_tasks.utils as cron_utils
from stores.models import Store

def run_missed_orders_cron():
    msg = []
    report_is_blank = True

    def trace(txt, important=False):
        print txt

        if txt.strip() == "":
            txt = "<br/>"

        if important:
            txt = "<strong>" + txt + "</strong>"

        msg.append(txt)

    trace("Notification about missing orders at FurniCloud", important=True)
    trace("-" * 60)
    orders_missing = __determine_potentially_missed_orders()    
    if orders_missing:
      report_is_blank = False
      trace("There are {0} potentially MISSING orders.".format(len(orders_missing)), important=True)
      for o in orders_missing:
        trace(str(o))
      trace("")
      trace("*NOTE: please verify that your orders have been entered. If the POS order is a quote, select a status of 'Dummy' for order in FurniCloud.", important=True)
      trace("-" * 60)
      trace("")

    trace("List of 10 most recent orders:", important=True)
    recent_orders = Order.objects.filter(status__exact='N').order_by('-order_date')[:10]
    for o in recent_orders:
       trace("Order {0}, created {1}, status: {2}, associate(s): {3}".format(o.number, 
          o.order_date.strftime("%m-%d-%Y"), o.get_status_display(), order_utils.get_order_associates(o)))
    trace("-" * 60)
    trace("")

    trace("*" * 60)
    trace("Please visits the 'Alerts' page on FurniCloud for full report".upper(), important=True)
    trace("*" * 60)
    
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
    err_msg = "MISSING order #{0}{1:04d}"

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
