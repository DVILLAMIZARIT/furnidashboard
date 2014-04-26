import django_filters as filters
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
