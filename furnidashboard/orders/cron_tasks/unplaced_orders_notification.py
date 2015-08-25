from orders.models import Order
from django.db.models import Q
import orders.utils as order_utils
import orders.cron_tasks.utils as cron_utils
from django.contrib.auth import get_user_model

def run_unplaced_orders_cron():
    msg = []
    report_is_blank = True

    def trace(txt, important=False):
        print txt

        if txt.strip() == "":
            txt = "<br/>"

        if important:
            txt = "<strong>" + txt + "</strong>"

        msg.append(txt)

    trace("Notification on unplaced orders at FurniCloud", important=True)
    trace("-" * 60)
    
    unplaced = order_utils.list_unplaced_orders() #Order.objects.unplaced_orders()
    if len(unplaced):
      trace("There are {0} UNPLACED orders (missing PO numbers):".format(len(unplaced)), important=True)
      report_is_blank = False

    for counter, o in enumerate(unplaced):
      trace("{0}) {1} unplaced. View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    
    if len(unplaced):
      trace("-" * 60)
      trace("")

    orders_no_ack_no = order_utils.list_unconfirmed_orders() #Order.objects.ordered_not_acknowledged()
    if len(orders_no_ack_no) > 0 :
      trace("There are {0} UNCONFIRMED orders (missing acknowledgement# from vendor):".format(len(orders_no_ack_no), important = True))
      report_is_blank = False

    for counter, o in enumerate(orders_no_ack_no):
      trace("{0}) {1} View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    if len(orders_no_ack_no) > 0 :
      trace("-" * 60)
      trace("-" * 60)

    #report_is_blank = True
    # send email notifications
    if not report_is_blank:
      cron_utils.send_emails (
        to=['lana@furnitalia.com', 'dima.aks@furnitalia.com', 'admin@furnitalia.com'],
        subject ="Notification about Unplaced Orders at FurniCloud",
        message="<br/>".join(msg)        
      )


def run_unplaced_orders_by_assoc_cron():

    def trace(txt, important=False):
        print txt

        if txt.strip() == "":
            txt = "<br/>"

        if important:
            txt = "<strong>" + txt + "</strong>"

        msg.append(txt)

    user_model = get_user_model()
    associates = user_model.objects.filter(Q(is_active=True) & Q(groups__name__icontains="associates"))

    for associate in associates:
        report_is_blank = True
        msg = []
        if len(associate.email):
            #process the following for each associate
            unplaced = order_utils.list_unplaced_orders(by_associate=associate) 
            if len(unplaced):
                report_is_blank = False
    		  
                trace("Notification on unplaced orders by {0}".format(associate.first_name + " " + associate.last_name), important=True)
                trace("-" * 60)

                trace("There are {0} UNPLACED special orders (missing PO numbers): ".format(len(unplaced)), important=True)
                for counter, o in enumerate(unplaced):
                    trace("{0}) {1} is unplaced. View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
    		  
                trace("-" * 60)
                trace("*** Please bring to Lana's or Dmitriy's attention that your orders need to be placed with the vendor ASAP! ***")
                trace("")

            orders_no_ack_no = order_utils.list_unconfirmed_orders(by_associate=associate) 
            if len(orders_no_ack_no):
                report_is_blank = False
                trace("There are {0} UNCONFIRMED orders  (missing acknowledgement# from vendor)".format(len(orders_no_ack_no), important = True))
                for counter, o in enumerate(orders_no_ack_no):
                    trace("{0}) {1} View order: http://cloud.furnitalia.com{2}".format(counter+1, o.number, o.get_absolute_url()))
                trace("-" * 60)
                trace("*** Please check status of the orders above. ***")
                trace("-" * 60)

    		#report_is_blank = True
    		# send email notifications
            if not report_is_blank:
                assoc_email = associate.email
                cron_utils.send_emails (
                    to=(assoc_email, 'admin@furnitalia.com'),
                    subject ="Notification about your Order status in FurniCloud",
                    message="<br/>".join(msg)
                )
