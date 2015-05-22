from django.views.generic import  DetailView, UpdateView
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django_tables2 import SingleTableView
from orders.models import OrderDelivery
from orders.tables import DeliveriesTable
import orders.forms as order_forms
import orders.utils as order_utils
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin

class DeliveriesTableView(LoginRequiredMixin, SingleTableView):
  model = OrderDelivery
  table_class = DeliveriesTable
  context_table_name = 'table' 
  template_name = "orders/delivery_list.html"
  paginate_by = 20 
  from_date = ""
  to_date = ""

  def get_queryset(self, **kwargs):
    qs = OrderDelivery.objects.filter(~Q(delivery_type='SELF'))

    date_range = ""
    try:
      date_range = self.request.GET['date_range']
      self.from_date, self.to_date = order_utils.get_date_range(date_range, self.request)    
    except KeyError, e:
      self.from_date, self.to_date = order_utils.get_date_range('week', self.request);
    
    lookup_kwargs = {
      '%s__gte' % 'scheduled_delivery_date': self.from_date,
      '%s__lt'  % 'scheduled_delivery_date': self.to_date,
    }
    qs = qs.filter(**lookup_kwargs)

    return qs

  def get_context_data(self, **kwargs):
    context = super(DeliveriesTableView, self).get_context_data(**kwargs)

    context['date_range_filter'] = order_forms.DateRangeForm(self.request.GET)
    
    date_range = ""
    if self.request.GET.has_key("date_range"):
      date_range = self.request.GET['date_range']

    if self.from_date and self.to_date:
      context['dates_caption'] = "{0} - {1}".format(self.from_date.strftime("%Y-%m-%d"), self.to_date.strftime("%Y-%m-%d"))

    return context
    
#-----------------------------------------------------------------------

class DeliveryDetailView(LoginRequiredMixin, DetailView):
  model = OrderDelivery
  context_object_name = "delivery"
  template_name = "orders/delivery_detail.html"

#-----------------------------------------------------------------------

class DeliveryDeleteView(LoginRequiredMixin, DeleteView):
  model = OrderDelivery
  success_url = reverse_lazy("delivery_list")

#-----------------------------------------------------------------------

class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
  model = OrderDelivery
  context_object_name = "delivery"
  template_name = "orders/delivery_update.html"
  form_class = order_forms.OrderDeliveryForm

  def get_form_kwargs(self):
    kwargs = super(DeliveryUpdateView, self).get_form_kwargs()
    kwargs.update({'request':self.request})
    return kwargs
