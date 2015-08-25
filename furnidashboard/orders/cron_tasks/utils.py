from django.core.mail.message import EmailMessage
from django.conf import settings
from datetime import datetime

def send_emails(to=None, subject="", message="", from_addr="admin@furnitalia.com"):
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
