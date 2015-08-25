from orders.models import Order
from django.db.models import Q
import orders.utils as order_utils
import orders.cron_tasks.utils as cron_utils
from django.contrib.auth import get_user_model

def run_unplaced_orders_cron():
    msg = []
    report_is_blank = True
 
    msg.append("<strong>Notification on unplaced orders at FurniCloud</strong>")
    msg.append("<br/>")
    
    unplaced = order_utils.list_unplaced_orders() #Order.objects.unplaced_orders()
    if len(unplaced):
      msg.append("<strong>There are {0} UNPLACED orders (missing PO numbers):</strong>".format(len(unplaced)))
      report_is_blank = False

    msg.append("<ul>")
    items = []
    for counter, o in enumerate(unplaced):
      items.append("<li>{0}) {1} unplaced. View order: http://cloud.furnitalia.com{2}</li>".format(counter+1, o.number, o.get_absolute_url()))
    msg.append("".join(items))
    msg.append("</ul>")
    
    if len(unplaced):
        msg.append("<br/>")

    orders_no_ack_no = order_utils.list_unconfirmed_orders() #Order.objects.ordered_not_acknowledged()
    if len(orders_no_ack_no) > 0 :
      msg.append("<strong>There are {0} UNCONFIRMED orders (missing acknowledgement# from vendor):</strong>".format(len(orders_no_ack_no)))
      report_is_blank = False

    msg.append("<ul>")
    items = []
    for counter, o in enumerate(orders_no_ack_no):
      items.append("<li>{0}) {1} View order: http://cloud.furnitalia.com{2}</li>".format(counter+1, o.number, o.get_absolute_url()))
    msg.append("".join(items))
    msg.append("</ul>")

    #report_is_blank = True
    # send email notifications
    if not report_is_blank:
      cron_utils.send_emails (
        to=['lana@furnitalia.com', 'd.aks@furnitalia.com', 'admin@furnitalia.com'],
        subject ="Notification about Unplaced Orders at FurniCloud",
        message="<br/>".join(msg)        
      )


def run_unplaced_orders_by_assoc_cron():

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
    		  
                msg.append("<strong>Notification on unplaced orders by {0}</strong>".format(associate.first_name + " " + associate.last_name))
                msg.append("<br/>")

                msg.append("<strong>There are {0} UNPLACED special orders (missing PO numbers):</strong>".format(len(unplaced)))
                msg.append("<ul>")
                items = []
                for counter, o in enumerate(unplaced):
                    items.append("<li>{0}) {1} is unplaced. View order: http://cloud.furnitalia.com{2}</li>".format(counter+1, o.number, o.get_absolute_url()))
                msg.append("".join(items))
                msg.append("</ul>")
    		  
                msg.append("<strong>*** Please bring to Lana's or Dmitriy's attention that your orders need to be placed with the vendor ASAP! ***</strong>")
                msg.append("<br/>")

            orders_no_ack_no = order_utils.list_unconfirmed_orders(by_associate=associate) 
            if len(orders_no_ack_no):
                report_is_blank = False
                msg.append("<strong>There are {0} UNCONFIRMED orders  (missing acknowledgement# from vendor)</strong>".format(len(orders_no_ack_no)))
                msg.append("<ul>")
                items = []
                for counter, o in enumerate(orders_no_ack_no):
                    items.append("<li>{0}) {1} View order: http://cloud.furnitalia.com{2}</li>".format(counter+1, o.number, o.get_absolute_url()))
                msg.append("".join(items))
                msg.append("</ul>")
                msg.append("<strong>*** Please check status of the orders above. ***</strong>")

    		#report_is_blank = True
    		# send email notifications
            if not report_is_blank:
                assoc_email = associate.email
                cron_utils.send_emails (
                    to=(assoc_email, 'admin@furnitalia.com'),
                    subject ="Notification about your Order status in FurniCloud",
                    message="<br/>".join(msg)
                )
