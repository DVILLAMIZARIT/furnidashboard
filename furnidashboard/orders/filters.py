import django_filters as filters
from .models import Order

CHOICES_FOR_STATUS_FILTER = [('', '--Any--')]
CHOICES_FOR_STATUS_FILTER.extend(list(Order.ORDER_STATUSES))

class OrderFilter(filters.FilterSet):
  status = filters.ChoiceFilter(choices=CHOICES_FOR_STATUS_FILTER)

  class Meta:
    model = Order
    fields = ['store', 'status', 'commission__associate']
