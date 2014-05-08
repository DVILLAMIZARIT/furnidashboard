import django_filters as filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from .models import Order

CHOICES_FOR_STATUS_FILTER = [('', '--Any--')]
CHOICES_FOR_STATUS_FILTER.extend(list(Order.ORDER_STATUSES))


class OrderFilter(filters.FilterSet):
  status = filters.ChoiceFilter(choices=CHOICES_FOR_STATUS_FILTER)

  def __init__(self, *args, **kwargs):
    super(OrderFilter, self).__init__(*args, **kwargs)
    self.helper = FormHelper()
    
    user_model = get_user_model() 
    self.filters['commission__associate'].field.queryset = user_model.objects.filter(Q(groups__name__icontains="associates") | Q(groups__name__icontains="managers" ))

    self.helper.layout = Layout(
      Fieldset(
        'Filter orders',
        Div(
          'store',
          'status',
          'commission__associate',
          Submit('submit', 'Filter'),
          css_class='well',
        ),
      ),
    )

  class Meta:
    model = Order
    fields = ['store', 'status', 'commission__associate']
