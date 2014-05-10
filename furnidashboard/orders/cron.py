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
    orders_missing = self._determine_potentially_missed_orders()
    if orders_missing:
      print "Possibly missing orders:"
      for o in orders_missing:
        print o
      print "-" * 20

    unplaced = Order.objects.unplaced_orders()
    print "Unplaced orders: " + unplaced.count()
    for o in unplaced:
      print o.number + " " + o.get_abosulte_url()
    print "-" * 20

    recent_orders = Order.objects.filter(status__exact='N').order_by('-created')[:5]
    print "Recent orders:"
    for o in recent_orders:
       print "Order {0} created at {1}".format(o.number, o.created)

  def _determine_potentially_missed_orders(self):
    launch_dt = datetime(2014, 6, 1)
    if settings.USE_TZ:
      launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())
    order_nums = sorted([o.number for o in Order.objects.filter(created__gte=launch_dt)])
    if order_nums:
      res = []
      first = int(order_nums[0])
      expected = first + 1
      for num in order_nums[1:]:
        if num != expected:
          res.append("Check for probably missing order: expected order with #{0}, first matched in sequence: #{1}".format(expected, num))
        else:
          expected = num + 1

    return res

    
