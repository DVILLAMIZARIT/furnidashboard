from django.conf import settings

from orders.models import Order
from django.db.models import Q
import orders.utils as order_utils
import orders.cron_tasks.utils as cron_utils
from django.contrib.auth import get_user_model


def run_unplaced_orders_cron():
    msg = []
    report_is_blank = True

    msg.append("<strong>-------- FurniCloud Order Alerts Notification --------- </strong>")
    msg.append("<br/>")

    #-----------------------------------
    # 1) Unplaced Orders Notification
    #-----------------------------------
    unplaced = order_utils.list_unplaced_orders()  # Order.objects.unplaced_orders()
    if len(unplaced):
        msg.append("<strong>UNPLACED orders: {0}</strong>".format(len(unplaced)))
        msg.append("The following orders are missing PO numbers:")
        report_is_blank = False

        items = []
        items.append("<table border=\"1\">")
        items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
        for counter, o in enumerate(unplaced):
            items.append(
                "<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                o.get_absolute_url()))
        items.append("</tbody></table>")
        msg.append("".join(items))

    if len(unplaced):
        msg.append("<br/>")

    #-----------------------------------
    # 2) Unconfirmed Orders Notification
    #-----------------------------------
    orders_no_ack_no = order_utils.list_unconfirmed_orders()  # Order.objects.ordered_not_acknowledged()
    if len(orders_no_ack_no) > 0:
        msg.append("<strong>UNCONFIRMED orders: {0} </strong>".format(
            len(orders_no_ack_no)))
        msg.append("The following orders are missing acknowledgement # from vendor:")
        report_is_blank = False

        items = []
        items.append("<table border=\"1\">")
        items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
        for counter, o in enumerate(orders_no_ack_no):
             items.append("<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                o.get_absolute_url()))
        items.append("</tbody></table>")
        msg.append("".join(items))

    if len(orders_no_ack_no):
        msg.append("<br/>")

    #-----------------------------------
    # 3) Crypton Approval Number Missing Notification
    #-----------------------------------
    orders_protection_plan_missing = Order.objects.protection_plan_inactive()
    if (len(orders_protection_plan_missing)):
        msg.append("<strong>Missing CRYPTON protection plan Confirmation Numbers: {0} Orders </strong>".format(
            len(orders_protection_plan_missing)))
        report_is_blank = False

        items = []
        items.append("<table border=\"1\">")
        items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
        for counter, o in enumerate(orders_protection_plan_missing):
             items.append("<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                o.get_absolute_url()))
        items.append("</tbody></table>")
        msg.append("".join(items))

    if len(orders_protection_plan_missing):
        msg.append("<br/>")

    #-----------------------------------
    # 4) Special Financing Confirmation Number Missing Notification
    #-----------------------------------
    orders_financing_missing = Order.objects.financing_unactivated()
    if (len(orders_financing_missing)):
        msg.append("<strong>Missing FINANCING Confirmation Numbers: {0} Orders </strong>".format(
            len(orders_financing_missing)))
        report_is_blank = False

        items = []
        items.append("<table border=\"1\">")
        items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
        for counter, o in enumerate(orders_financing_missing):
             items.append("<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                o.get_absolute_url()))
        items.append("</tbody></table>")
        msg.append("".join(items))

    if len(orders_financing_missing):
        msg.append("<br/>")

    # report_is_blank = True
    # send email notifications
    if not report_is_blank:
        cron_utils.send_emails (
            to=['pearl@furnitalia.com', 'd.aks@furnitalia.com', 'admin@furnitalia.com'],
            subject="FurniCloud Order Alerts",
            message="<br/>".join(msg)
        )


def run_unplaced_orders_by_assoc_cron():
    user_model = get_user_model()
    associates = user_model.objects.filter(Q(is_active=True) & Q(groups__name__icontains="associates"))

    for associate in associates:
        report_is_blank = True
        msg = []
        if len(associate.email) and associate.email in settings.CRON_EMAIL_NOTIFICATION_LIST:
            # process the following for each associate

            #-----------------------------------
            # 1) Unplaced Orders Notification
            #-----------------------------------
            unplaced = order_utils.list_unplaced_orders(by_associate=associate)
            if len(unplaced):
                report_is_blank = False

                msg.append("<strong>-------- FurniCloud Alerts for Orders owned by {0} -------- </strong>".format(
                    associate.first_name + " " + associate.last_name))
                msg.append("<br/>")

                msg.append("<strong>UNPLACED orders: {0}</strong>".format(len(unplaced)))
                msg.append("The following orders are missing PO numbers:")

                items = []
                items.append("<table border=\"1\">")
                items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
                for o in unplaced:
                    items.append(
                        "<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                        o.get_absolute_url()))
                items.append("</tbody></table>")
                msg.append("".join(items))
                msg.append("<br/>")
                msg.append(
                    "<strong>*** Please bring to Lana's/Ruth or Dmitriy's attention that your orders need to be placed with the vendor ASAP! ***</strong>")
                msg.append("<br/>")

            #-----------------------------------
            # 2) Unconfirmed Orders Notification
            #-----------------------------------
            orders_no_ack_no = order_utils.list_unconfirmed_orders(by_associate=associate)
            if len(orders_no_ack_no) > 0:
                msg.append("<strong>UNCONFIRMED orders: {0} </strong>".format(
                    len(orders_no_ack_no)))
                msg.append("The following orders are missing acknowledgement # from vendor:")
                report_is_blank = False

                items = []
                items.append("<table border=\"1\">")
                items.append("<thead><th>Order #</th><th>Order Date</th><th>Link</th></thead><tbody>")
                for counter, o in enumerate(orders_no_ack_no):
                     items.append("<tr><td>{0}</td><td>{1}</td><td>http://cloud.furnitalia.com{2}</td></tr>".format(o.number, o.order_date.strftime("%m-%d-%Y"),
                                                                                                        o.get_absolute_url()))
                items.append("</tbody></table>")
                msg.append("".join(items))
                msg.append("<br/>")


            # -------------------------------+
            # send email notifications       |
            # -------------------------------+
            if not report_is_blank:
                assoc_email = associate.email
                cron_utils.send_emails(
                    to=(assoc_email),
                    subject="Alerts on your Orders in FurniCloud",
                    message="<br/>".join(msg)
                )
