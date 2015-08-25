from django.utils import timezone
from django.core.mail.message import EmailMessage
from django.conf import settings
from django_cron import CronJobBase, Schedule
from django.contrib.auth import get_user_model
from django.db.models import Q
from datetime import datetime
from orders.models import Order
import orders.utils as order_utils
from stores.models import Store

class FurnCronJob(CronJobBase):
  MIN_NUM_FAILURES = 3

  def trace(self, txt, important=False):
    print txt

    if txt.strip() == "":
      txt = "<br/>"

    if important:
      txt = "<strong>" + txt + "</strong>"

    self.msg.append(txt)

  def send_emails(self, to=None, subject="", message="", from_addr="admin@furnitalia.com"):
    if len(message.strip()) == 0 :
      return

    if to == None :
      to = settings.CRON_EMAIL_NOTIFICATION_LIST

    report_date = datetime.now().strftime('%m-%d-%Y')    
    if subject == "":
      subject = "FurniCloud Report (" + report_date + ")"
    else:
      subject = subject + " | " + report_date
    
    message = 'Report created on ' + report_date + '<br/><br/>' + message
    email_msg = EmailMessage(subject, message, from_addr, to) 
    email_msg.content_subtype = "html"
    email_msg.send()

  # def send_emails(self):

  #   report_date = datetime.now().strftime('%m-%d-%Y')
  #   to = ['akhmirem@gmail.com', 'lana@furnitalia.com', 'd.aks@furnitalia.com', 'pearl@furnitalia.com', 'ruth@furnitalia.com', 'jenn@furnitalia.com', 'jamie@furnitalia.com']
  #   self.msg[:0] = ['Report created on ' + report_date, ""]
  #   email_msg = EmailMessage("FurniCloud Report (" + report_date + ")", "<br/>".join(self.msg), "admin@furnitalia.com", to) 
  #   email_msg.content_subtype = "html"
  #   email_msg.send()


class UnplacedOrderCronJob(FurnCronJob):
  code = 'orders.cron.UnplacedOrderCronJob'  
  msg = []
  report_is_blank = True

  #this job will run only at 6am
  RUN_AT_TIMES = ['06:00']   
  schedule = Schedule(run_at_times=RUN_AT_TIMES) #, run_every_mins=RUN_EVERY_MINS)  

  def do(self):

    self.trace("Notification on unplaced orders at FurniCloud", important=True)
    self.trace("-" * 60)
    
    unplaced = order_utils.list_unplaced_orders() #Order.objects.unplaced_orders()
    if len(unplaced):
      self.trace("There are {0} UNPLACED orders (missing PO numbers):".format(len(unplaced)), important=True)
      self.report_is_blank = False

    for counter, o in enumerate(unplaced):
      self.trace("{0}) {1} unplaced. View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    
    if len(unplaced):
      self.trace("-" * 60)
      self.trace("")

    orders_no_ack_no = order_utils.list_unconfirmed_orders() #Order.objects.ordered_not_acknowledged()
    if len(orders_no_ack_no) > 0 :
      self.trace("There are {0} UNCONFIRMED orders (missing acknowledgement# from vendor):".format(len(orders_no_ack_no), important = True))
      self.report_is_blank = False

    for counter, o in enumerate(orders_no_ack_no):
      self.trace("{0}) {1} View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    if len(orders_no_ack_no) > 0 :
      self.trace("-" * 60)
      self.trace("-" * 60)

    #self.report_is_blank = True
    # send email notifications
    if not self.report_is_blank:
      self.send_emails (
        to=['lana@furnitalia.com', 'dima.aks@furnitalia.com', 'admin@furnitalia.com'],
        subject ="Notification about Unplaced Orders at FurniCloud",
        message="<br/>".join(self.msg)        
      )

class UnplacedOrderByAssocCronJob(UnplacedOrderCronJob):
  code = 'orders.cron.UnplacedOrderByAssocCronJob'  

  # cron job will run at 6:30am
  RUN_AT_TIMES = ['06:30']
  #RUN_EVERY_MINS = 1 # every minute
  schedule = Schedule(run_at_times=RUN_AT_TIMES) #, run_every_mins=RUN_EVERY_MINS)  

  def do(self):    

    user_model = get_user_model()
    associates = user_model.objects.filter(Q(is_active=True) & Q(groups__name__icontains="associates"))

    for associate in associates:
      self.report_is_blank = True
      self.msg = []
      if len(associate.email):
        #process the following for each associate
    		unplaced = order_utils.list_unplaced_orders(by_associate=associate) 
    		if len(unplaced):
    			self.report_is_blank = False
    		  
    			self.trace("Notification on unplaced orders by {0}".format(associate.first_name + " " + associate.last_name), important=True)
    			self.trace("-" * 60)

    			self.trace("There are {0} UNPLACED special orders (missing PO numbers): ".format(len(unplaced)), important=True)
    			for counter, o in enumerate(unplaced):
    				self.trace("{0}) {1} is unplaced. View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    		  
    			self.trace("-" * 60)
    			self.trace("*** Please bring to Lana's or Dmitriy's attention that your orders need to be placed with the vendor ASAP! ***")
    			self.trace("")

    		orders_no_ack_no = order_utils.list_unconfirmed_orders(by_associate=associate) 
    		if len(orders_no_ack_no):
    		  self.report_is_blank = False
    		  self.trace("There are {0} UNCONFIRMED orders  (missing acknowledgement# from vendor)".format(len(orders_no_ack_no), important = True))
    		  for counter, o in enumerate(orders_no_ack_no):
    			self.trace("{0}) {1} View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    		  self.trace("-" * 60)
    		  self.trace("*** Please check status of the orders above. ***")
    		  self.trace("-" * 60)

    		#self.report_is_blank = True
    		# send email notifications
    		if not self.report_is_blank:
    		  assoc_email = associate.email
    		  self.send_emails (
    			to=(assoc_email, 'admin@furnitalia.com'),
    			subject ="Notification about your Order status in FurniCloud",
    			message="<br/>".join(self.msg)
    		  )

  

class OrderCronJob(FurnCronJob):
  code = 'orders.cron.OrderCronJob'
  msg = []
  report_is_blank = True

  # cron job will run at 7:00am
  RUN_AT_TIMES = ['07:00']
  #RUN_EVERY_MINS = 100 # every minute
  schedule = Schedule(run_at_times=RUN_AT_TIMES) #, run_every_mins=RUN_EVERY_MINS)  

  def do(self):

    self.trace("Notification about missing orders at FurniCloud", important=True)
    self.trace("-" * 60)
    orders_missing = self.determine_potentially_missed_orders()    
    if orders_missing:
      self.report_is_blank = False
      self.trace("There are {0} potentially MISSING orders.".format(len(orders_missing)), important=True)
      for o in orders_missing:
        self.trace(str(o))
      self.trace("")
      self.trace("*NOTE: please verify that your orders have been entered. If the POS order is a quote, select a status of 'Dummy' for order in FurniCloud.", important=True)
      self.trace("-" * 60)
      self.trace("")

    self.trace("List of 10 most recent orders:", important=True)
    recent_orders = Order.objects.filter(status__exact='N').order_by('-order_date')[:10]
    for o in recent_orders:
       self.trace("Order {0}, created {1}, status: {2}, associate(s): {3}".format(o.number, 
          o.order_date.strftime("%m-%d-%Y"), o.get_status_display(), order_utils.get_order_associates(o)))
    self.trace("-" * 60)
    self.trace("")

    self.trace("*" * 60)
    self.trace("Please visits the 'Alerts' page on FurniCloud for full report".upper(), important=True)
    self.trace("*" * 60)
    
    #self.report_is_blank = True
    # send email notifications
    if not self.report_is_blank:
      self.send_emails(message="<br/>".join(self.msg))

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
