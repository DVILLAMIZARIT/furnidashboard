from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

class OrderManager(models.Manager):
  launch_dt = datetime(2014, 5, 1)
  if settings.USE_TZ:
    launch_dt = timezone.make_aware(launch_dt, timezone.get_current_timezone())

  def get_qs(self):
    qs = super(OrderManager, self).get_queryset().filter(~Q(status='I'))
    return qs
   
  def get_dated_qs(self, start, end):
    lookup_kwargs = {
        '%s__gte' % 'order_date': start -  timedelta(minutes=1),
        '%s__lt' % 'order_date': end,
    }
    return super(OrderManager, self).get_queryset().filter(**lookup_kwargs)
  
  def unplaced_orders(self):
    """ queryset that find unplaced special orders, for which there is no PO number specified """
    qs = self.get_qs()
    return qs.filter(Q(orderitem__in_stock=False) & Q(orderitem__po_num="")).distinct()

  def open_orders(self):
    """ Returns a queryset with open orders (for which status is not 'Closed') """
    return self.get_qs().filter(~Q(status='C'))
    
  def ordered_not_acknowledged(self):
    """ returns a queryset for order that have been placed with vendor but missing the acknowledgement number """
    qs = self.get_qs()
    return qs.filter(~Q(orderitem__po_num="") & Q(orderitem__ack_num="")).distinct()
  
  def special_acknowledged_no_eta(self):
    """ Returns a queryset for special orders that have acknowledgement number but missing ETA date """
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['O', 'P']) & ~Q(orderitem__ack_num="") & Q(orderitem__eta__isnull=True)).distinct()
  
  def special_eta_passed_not_received(self):
    """ returns a queryset for special orders for which ETA has already passed, but item status is not 'Received' """
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['O', 'P']) & Q(orderitem__eta__gte=datetime.now())).distinct()
  
  def not_yet_delivered(self):
    """ returns a queryset for orders that have not been delivered """
    qs = self.get_qs()
    return qs.filter(Q(orderitem__status__in=['S', 'R']))

  def commissions_unpaid(self):
    """ returns a queryset for orders for which commissions have not been paid """
    qs = self.get_qs()
    return qs.filter(Q(status__in=['D', 'C']) & Q(commission__paid=False))

  def protection_plan_inactive(self):
    """ returns a queryset for orders with protection plan purchased but unactivated """
    qs = self.get_qs()
    return qs.filter(Q(protection_plan=True) & Q(orderitemprotectionplan__isnull=True))

  def financing_unactivated(self):
    """ returns a queryset for orders with financing option selected but unactivated """
    qs = self.get_qs()
    return qs.filter(Q(financing_option=True) & Q(orderfinancing__isnull=True))