from django.utils import timezone
from django.conf import settings
from django_cron import CronJobBase, Schedule
from .models import Order
from stores.models import Store
from datetime import datetime

class OrderCronJob(CronJobBase):
  RUN_EVERY_MINS = 1 # every hours
  MIN_NUM_FAILURES = 3

  schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
  code = 'orders.cron.OrderCronJob'

  def do(self):
    print "Checking for MISSING orders:"
    orders_missing = self.determine_potentially_missed_orders()
    print "{0} potentially missed order(s)".format(len(orders_missing))
    if orders_missing:
      for o in orders_missing:
        print o
      print "-" * 20

    unplaced = Order.objects.unplaced_orders()
    print "Checking for UNPLACED orders: "
    print "{0} item(s)".format(unplaced.count())
    for o in unplaced:
      print "#{0} unplaced. View details: {1}".format(o.number, o.get_absolute_url())
    print "-" * 20

    recent_orders = Order.objects.filter(status__exact='N').order_by('-order_date')[:5]
    print "5 most recent orders:"
    for o in recent_orders:
       print "Order {0}, created {1}".format(o.number, o.order_date.strftime("%m-%d-%Y"))
    print "-" * 20
       
    orders_no_ack_no = Order.objects.ordered_not_acknowledged()
    print "Special Orders, acknowledgement not received from vendor:"
    print "{0} orders_no_ack_no(s)".format(orders_no_ack_no.count())
    for o in orders_no_ack_no:
      print "#{0} order item(s) not acknowledged. View order: {1}".format(o.number, o.get_absolute_url())
    print "-" * 20

  def determine_potentially_missed_orders(self):
    res = []
    launch_dt = datetime(2014, 6, 1)
    if settings.USE_TZ:
      launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())

    orders = Order.objects.filter(order_date__gte=launch_dt, number__istartswith="SO") 
    
    sac_orders = orders.filter(store=Store.objects.get(name="Sacramento"))
    fnt_orders = orders.filter(store=Store.objects.get(name="Roseville"))

    sac_order_nums = sorted(map(lambda o: int(o.number[-4:]), sac_orders))
    fnt_order_nums = sorted(map(lambda o: int(o.number[-4:]), fnt_orders))
    
    lst = self.find_skipped_order_nums(sac_order_nums, "SO-01-")
    if lst:
      res += lst

    lst = self.find_skipped_order_nums(fnt_order_nums, "SO-03-")
    if lst:
      res += lst

    return res

  def find_skipped_order_nums(self, order_nums, prefix):

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
