import django_filters as filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field
from .models import ClaimStatus, Claim

CHOICES_FOR_STATUS_FILTER = [('', '--Any--')]
CHOICES_FOR_STATUS_FILTER.extend(list(ClaimStatus.CLAIM_STATUSES))


class ClaimFilter(filters.FilterSet):
  claim_status = filters.ChoiceFilter(choices=CHOICES_FOR_STATUS_FILTER)

  def __init__(self, *args, **kwargs):
    super(ClaimFilter, self).__init__(*args, **kwargs)
        
    #user_model = get_user_model()
    #self.filters['commission__associate'].field.queryset = user_model.objects.filter(Q(groups__name__icontains="associates") | Q(groups__name__icontains="managers" ))

    self.helper = FormHelper()
    self.helper.form_class = 'form-inline'
    self.helper.field_template = 'bootstrap3/layout/inline_field.html'
    self.helper.layout = Layout(
        Div(
          'store',
          'status',
          'commission__associate',
          Submit('submit', 'Filter', css_class='btn-default'),
          css_class = 'well'
        )
    )

    #self.form.fields['store'].widget.attrs['placeholder'] = 'Store'

  class Meta:
    model = Claim
    fields = ['claim_status']
