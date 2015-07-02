from django import forms
from datetime import datetime
import calendar
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field, HTML
  
MONTH_CHOICES = []
for i in xrange(1, 13):
	MONTH_CHOICES.append((i, calendar.month_name[i]))
	
YEAR_CHOICES = []
for i in xrange(2013, datetime.now().year + 1):
	YEAR_CHOICES.append((i, i))
		
class MonthYearFilterForm(forms.Form):
  month = forms.ChoiceField(label="Select month", required=False, choices=MONTH_CHOICES)
  year = forms.ChoiceField(label="Select year", required=False, choices=YEAR_CHOICES)

  def __init__(self, *args, **kwargs):
    super(MonthYearFilterForm, self).__init__(*args, **kwargs)
        
    self.helper = FormHelper()
    self.form_tag = False
    self.disable_csrf = True
    self.helper.form_class = 'form-inline'
    self.helper.field_template = 'bootstrap3/layout/inline_field.html'
    self.helper.layout = Layout(
        Div(
        	HTML (
        		'<h3>Select date range</h3>'
          	),
			'month',
			'year',
			Submit('submit', 'Filter', css_class='btn-default'),
			css_class = 'well'
        )
    )

  
