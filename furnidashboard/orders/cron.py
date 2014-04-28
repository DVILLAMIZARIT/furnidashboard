from django_cron import CronJobBase, Schedule
from .models import Order

class OrderCronJob(CronJobBase):
  RUN_EVERY_MINS = 1 # every hours
  MIN_NUM_FAILURES = 3

  schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
  code = 'orders.cron.OrderCronJob'

  def do(self):
    recent_orders = Order.objects.filter(status__exact='N').order_by('-created')[:5]
    for o in recent_orders:
       print "Order {0} created at {1}".format(o.number, o.created)
