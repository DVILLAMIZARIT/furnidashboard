import re
from django.db.models import Q
from django_tables2 import RequestConfig, SingleTableView 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.mixins import LoginRequiredMixin
import core.utils as utils
from customers.models import Customer
from orders.models import Order, OrderDelivery
from orders.views.deliveries import DeliveriesTableView
from orders.tables import OrderTable, UnpaidCommissionsTable
from commissions.models import Commission

#TODO: add ETA Overdue Order Items alert

class AlertsTableView(LoginRequiredMixin, SingleTableView):
  model = Order
  table_class = OrderTable
  template_name = "core/alerts_table.html"
  subtitle = ""

  def get_context_data(self, **kwargs):
    context = super(AlertsTableView, self).get_context_data(**kwargs)
    context['alert_title'] = self.subtitle
    return context

class UnplacedOrderTableView(AlertsTableView):
  subtitle = 'Unplaced Orders'

  def get_queryset(self, **kwargs):
    return  Order.objects.unplaced_orders()

class UnpaidDeliveriesTableView(DeliveriesTableView):
  template_name = "core/alerts_table.html"
  subtitle = 'Unpaid Deliveries'

  def get_queryset(self, **kwargs):
    return utils.get_unpaid_deliveries_queryset() 

  def get_context_data(self, **kwargs):
    context = super(UnpaidDeliveriesTableView, self).get_context_data(**kwargs)
    context['alert_title'] = self.subtitle
    return context

class OrderedUnacknowledgedOrdersTableView(AlertsTableView):
  subtitle = "Unconfirmed special orders"
  def get_queryset(self, **kwargs):
    return Order.objects.ordered_not_acknowledged()

class UnpaidCommissionsTableView(AlertsTableView):
  model = Commission
  subtitle = "Unpaid Commissions"
  table_class = UnpaidCommissionsTable

  def get_table_data(self):
    return utils.get_unpaid_commissions_data() 

class CryptonProtectionAlertTableView(AlertsTableView):
  model = Order
  subtitle = "Unactivated Crypton Protection"

  def get_table_data(self):
    return Order.objects.protection_plan_inactive() 

class OrderFinancingAlertTableView(AlertsTableView):
  model = Order
  subtitle = "Unactivated Order Financing"

  def get_table_data(self):
    return Order.objects.financing_unactivated()     


# SEARCH VIEW and RELATED FUNCTIONS
def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S)').findall, normspaces=re.compile(r'\s{2,}').sub):
  """ Splits the query string in individual keywords, getting rid of unnecessary spaces and grouping quoted words together.
      Example:
      >>> normalize_query(' soem random words "with quotes " and    spaces')
      >>> ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
  """

  return [normspaces(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
  """ Returns a query that is a combination of Q objects. That combination aims to search keywords within a model by testing the given search fields
  """

  query = None # Query to search for every search term

  terms = normalize_query(query_string)
  for term in terms:
    or_query = None # Query to search for a given term in each field
    for field_name in search_fields:
      q = Q(**{"%s__icontains" % field_name: term})
      if or_query is None:
        or_query = q
      else:
        or_query = or_query | q
    if query is None:
      query = or_query
    else:
      query = query & or_query
  return query

@login_required 
def search(request):
  query_string = ''
  found_entries = None
  if request.GET:
    query_string = request.GET.get('q', '').strip()

    if query_string:

      entry_query = get_query(query_string, ['number',]) #, 'comments',])
      found_orders = Order.objects.filter(entry_query).order_by('-created')

      entry_query = get_query(query_string, ['first_name', 'last_name', 'email'])
      found_customers = Customer.objects.filter(entry_query).order_by('-last_name')

      return render(request, 'search/search_results.html', 
        {'query_string': query_string, 
         'found_orders': found_orders,
         'found_customers':found_customers,
        },
      )
