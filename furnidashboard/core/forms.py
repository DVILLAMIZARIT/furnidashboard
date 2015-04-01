from django import forms
from datetime import datetime
from bootstrap_toolkit.widgets import BootstrapDateInput
import calendar
  
MONTH_CHOICES = []
for i in xrange(1, 13):
	MONTH_CHOICES.append((i, calendar.month_name[i]))
	
YEAR_CHOICES = []
for i in xrange(2013, datetime.now().year + 1):
	YEAR_CHOICES.append((i, i))
		
class MonthYearFilterForm(forms.Form):
  month = forms.ChoiceField(label="Select month", required=False, choices=MONTH_CHOICES)
  year = forms.ChoiceField(label="Select year", required=False, choices=YEAR_CHOICES)
  
