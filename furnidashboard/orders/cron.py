from django.utils import timezone
from django.conf import settings
from django_cron import CronJobBase, Schedule
from .models import Order
from datetime import datetime

class OrderCronJob(CronJobBase):
  RUN_EVERY_MINS = 1 # every hours
  MIN_NUM_FAILURES = 3

  schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
  code = 'orders.cron.OrderCronJob'

  def do(self):
    print "Checking for missing orders:"
    orders_missing = self._determine_potentially_missed_orders()
    print "{0} item(s)".format(len(orders_missing))
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
    print "Recent orders:"
    for o in recent_orders:
       print "Order {0} created at {1}".format(o.number, o.order_date.strftime("%m-%d-%Y"))
       
    orders_no_ack_no = Order.objects.ordered_not_acknowledged()
    print "Special Orders, acknowledgement not received from vendor:"
    print "{0} orders_no_ack_no(s)".format(orders_no_ack_no.count())
    for o in orders_no_ack_no:
      print "#{0} order item(s) have not yet been acknowledged. View details: {1}".format(o.number, o.get_absolute_url())
    print "-" * 20

  def _determine_potentially_missed_orders(self):
    res = []
    launch_dt = datetime(2014, 6, 1)
    if settings.USE_TZ:
      launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())
    order_nums = sorted([o.number for o in Order.objects.filter(order_date__gte=launch_dt)])
    if order_nums:
      first = int(order_nums[0])
      expected = first + 1
      for num in order_nums[1:]:
        num = int(num)
        if num != expected:
          res.append("Potentially missing order: EXPECTED order #{0} - not found; next in sequence: #{1}".format(expected, num))
          expected = expected + 1
          while expected < num:
            res.append("Potentially missing order: EXPECTED order #{0} - not found; next in sequence: #{1}".format(expected, num))
            expected = expected + 1
          if expected <= num:
            expected = expected + 1
        else:
          expected = num + 1

    return res
