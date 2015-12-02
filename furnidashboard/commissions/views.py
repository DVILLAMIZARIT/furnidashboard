from datetime import datetime
from django.views.generic import ListView
from orders.models import Order
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin
import core.forms as core_forms
import core.utils as core_utils
from django_tables2 import RequestConfig
import orders.utils as order_utils
from orders.tables import SalesByAssociateWithBonusTable

class BonusMonthlyReportView(PermissionRequiredMixin, ListView):
  model = Order
  context_object_name = "bonus_list"
  template_name = "commissions/bonus_report.html"
  from_date = ""
  to_date = ""

  required_permissions = (
    'orders.view_sales',
  )
  
  def get_queryset(self, **kwargs):
    month = year = ""
    try:
      month = int(self.request.GET['month'])
      year = int(self.request.GET['year'])  
      self.from_date, self.to_date = core_utils.get_month_date_range(month, year)
    except (KeyError, TypeError) as e:
      self.from_date, self.to_date = core_utils.get_current_month_date_range()
    
    qs = Order.objects.get_dated_qs(self.from_date, self.to_date)
    
    return qs

  def get_context_data(self, **kwargs):
    context = super(BonusMonthlyReportView, self).get_context_data(**kwargs)

    initial = {'month': datetime.now().month, 'year': datetime.now().year }
    params = dict(initial.items() + self.request.GET.items())
    context['date_range_filter'] = core_forms.MonthYearFilterForm(params)

    orders = context[self.context_object_name]

    attrs = {'old_bonus' : False}
    #import pdb; pdb.set_trace()
    if self.from_date < datetime(2015, 02, 01): #new bonus start date - 02/01/2015!!!
      attrs['old_bonus'] = True

    sales_by_assoc_data, tmp_res = order_utils.get_sales_data_from_orders(orders, **attrs)
    sales_by_assoc = SalesByAssociateWithBonusTable(sales_by_assoc_data)

    RequestConfig(self.request).configure(sales_by_assoc)
    context['sales_by_associate'] = sales_by_assoc 

    return context
