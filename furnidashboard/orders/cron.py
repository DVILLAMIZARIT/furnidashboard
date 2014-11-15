from django.utils import timezone
from django.conf import settings
from django_cron import CronJobBase, Schedule
from .models import Order
from stores.models import Store
from datetime import datetime
from django.core.mail.message import EmailMessage

class OrderCronJob(CronJobBase):
  RUN_EVERY_MINS = 1 # every hours
  MIN_NUM_FAILURES = 3

  schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
  code = 'orders.cron.OrderCronJob'
  msg = []

  def do(self):

    self.msg = []

    self.trace("Checking for MISSING orders:", important=True)
    orders_missing = self.determine_potentially_missed_orders()
    self.trace("{0} potentially missed order(s)".format(len(orders_missing)), important=True)
    if orders_missing:
      for o in orders_missing:
        self.trace(str(o))
    self.trace("-" * 40)
    self.trace("")

    self.trace("Checking for UNPLACED orders: ", important=True)
    unplaced = Order.objects.unplaced_orders()
    self.trace("{0} item(s)".format(unplaced.count()), important=True)
    for o in unplaced:
      self.trace("#{0} unplaced. View details: http://cloud.furnitalia.com{1}".format(o.number, o.get_absolute_url()))
    self.trace("-" * 40)
    self.trace("")

    self.trace("5 most recent orders:", important=True)
    recent_orders = Order.objects.filter(status__exact='N').order_by('-order_date')[:5]
    for o in recent_orders:
       self.trace("Order {0}, created {1}, status {2}".format(o.number, o.order_date.strftime("%m-%d-%Y"), o.get_status_display()))
    self.trace("-" * 40)
    self.trace("")
       
    self.trace("Special Orders, acknowledgement not received from vendor:", important=True)
    orders_no_ack_no = Order.objects.ordered_not_acknowledged()
    self.trace("{0} orders_no_ack_no(s)".format(orders_no_ack_no.count(), important = True))
    for o in orders_no_ack_no:
      self.trace("#{0} order item(s) not acknowledged. View order: http://cloud.furnitalia.com{1}".format(o.number, o.get_absolute_url()))
    self.trace("-" * 40)

    # SEND EMAIL
    self.send_emails()

  def determine_potentially_missed_orders(self):
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
    
    lst = self.find_skipped_order_nums(sac_order_nums, "SO-1")
    if lst:
      res += lst

    lst = self.find_skipped_order_nums(fnt_order_nums, "SO-3")
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

  def trace(self, txt, important=False):
    print txt

    if txt.strip() == "":
      txt = "<br/>"

    if important:
      txt = "<strong>" + txt + "</strong>"

    self.msg.append(txt)

  def send_emails(self):

    report_date = datetime.now().strftime('%m-%d-%Y')
    to = ['akhmirem@gmail.com', 'lana@furnitalia.com', 'd.aks@furnitalia.com']
    self.msg[:0] = ['Report created on ' + report_date, ""]
    email_msg = EmailMessage("FurniCloud Report (" + report_date + ")", "<br/>".join(self.msg), "admin@furnitalia.com", to) 
    email_msg.content_subtype = "html"
    email_msg.send()
