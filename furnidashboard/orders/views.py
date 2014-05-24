from django.views.generic import ListView, DetailView, UpdateView, RedirectView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView, WeekArchiveView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig, SingleTableView
from django.db.models import Q
from datetime import timedelta, date, datetime
from .models import Order, OrderItem, OrderDelivery
from .tables import OrderTable, UnplacedOrdersTable, SalesByAssociateTable, DeliveriesTable, SalesTotalsTable
from .forms import OrderForm, CustomerFormSet, CommissionFormSet, ItemFormSet, get_ordered_items_formset, DeliveryFormSet, get_deliveries_formset, get_commissions_formset, OrderDeliveryForm, OrderItemFormHelper
from .filters import OrderFilter
from customers.models import Customer
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import core.utils as utils
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin
import orders.utils as order_utils

class UnplacedOrderTableView(SingleTableView):
  model = Order
  table_class = OrderTable
  template_name = "orders/order_table.html"

  def get_queryset(self, **kwargs):
    return  Order.objects.unplaced_orders() #select_related().filter(Q(status=None) | Q(status='N') | (Q(orderitem__in_stock=False) & (Q(orderitem__po_num__isnull=True) | Q(orderitem__po_num="")))).distinct()

class OrderDetailView(PermissionRequiredMixin, DetailView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_detail.html"

  required_permissions = (
    'orders.view_orders',
  )

class OrderDeleteView(PermissionRequiredMixin, DeleteView):
  model = Order
  context_object_name = "order"
  success_url = reverse_lazy("order_list")

  required_permissions = (
    'orders.delete_order',
  )

class OrderUpdateView(PermissionRequiredMixin, UpdateView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_update.html"
  form_class = OrderForm

  required_permissions = (
    'orders.change_order',
  )

  def get(self, request, *args, **kwargs):
    """ 
    Handle GET requests and instantiate blank version of the form
    and it's inline formsets
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    self.request = request
    
    if not request.user.has_perm('orders.update_status'):
      #disable order status for staff person without privilege
      form.fields['status'].widget.attrs['readonly'] = 'readonly'
    
    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers") 

    extra = 1 if self.object.commission_set.count() == 0 else 0  #if no commissions were saved for this order, add a blank form
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(instance=self.object, prefix="commissions")
    
    extra = 1 if self.object.orderdelivery_set.count() == 0 else 0
    DeliveriesFormSet = get_deliveries_formset(extra=extra, max_num=100, request=self.request)
    delivery_form = DeliveriesFormSet(instance=self.object, prefix="deliveries")

    # prevent empty form showing up if no items were recorded for the order
    # specify at least 1 extra of no items are set
    extra = 1 if self.object.orderitem_set.count() == 0 else 0
    SoldItemsFormSet = get_ordered_items_formset(extra=extra, max_num=100)
    items_form = SoldItemsFormSet(instance=self.object, prefix="ordered_items")
    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
    }
    context = self.get_context_data()
    context.update(extra_forms)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    self.request = request
    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")
    commissions_form = CommissionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="commissions")
    items_form = ItemFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="ordered_items")
    DeliveriesFormSet = get_deliveries_formset(extra=0, max_num=100, request=self.request)
    delivery_form = DeliveriesFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="deliveries")
    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
    }

    #check if forms are valid
    forms_valid = form.is_valid()
    if forms_valid and commissions_form.has_changed():
      forms_valid = commissions_form.is_valid()
    if forms_valid and items_form.has_changed():  
      forms_valid = items_form.is_valid()
    if forms_valid :
      #import pdb; pdb.set_trace()
      for form in [f for f in delivery_form.forms if f.has_changed()]: # and  f not in delivery_form.deleted_forms]:  
        forms_valid = form.is_valid()
        if not forms_valid:
          break
      
    if forms_valid:
      return self.form_valid(**forms)
    else:
      return self.form_invalid(**forms)

  def form_valid(self, *args, **kwargs):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    form = kwargs['form']
    customer_form = kwargs['customer_form']
    items_form = kwargs['items_form']
    commissions_form = kwargs['commissions_form']
    delivery_form = kwargs['delivery_form']
    
    orig_status = self.object.status
    self.object = form.save(commit=False)

    # flags
    BR_passed = True
    new_customer=False

    # import pdb; pdb.set_trace()

    if not form.data['status'] :
      messages.error(self.request, "Please enter order status'")
      BR_passed = False

    # validate customer
    if BR_passed:
      if form.cleaned_data['customer'] is None:
        if customer_form.is_valid():
          # check that first and last name are filled
          try:
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, "Please select existing customer or fill in new customer information!")
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, "Please select existing customer or fill in new customer information!")
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer form information!")
          BR_passed = False
  
#    # validate items
#    if BR_passed: 
#      for ind in xrange(items_form.total_form_count()):
#        try:
#          if items_form.cleaned_data[ind]['description'] is None:
#            BR_passed = False
#        except KeyError:
#          BR_passed = False
#
#      if not BR_passed:
#        messages.error(self.request, "Please enter sold item(s) description")

    if BR_passed: 
      
      if not self.request.user.has_perm('orders.update_status'):
        if orig_status:
          self.object.status = orig_status #reset previous value
          messages.warning(self.request, "You don't have permission to change order status. Order status was reset to previous value.")
        
      #save order
      self.object.save()
      
      # save customer
      if new_customer:
        cust = customer_form[0].save()
        self.object.customer = cust

      # save items
      if items_form.has_changed():
        items_form.instance = self.object
        items_form.save()

      # save commissions
      if commissions_form.has_changed():
        commissions_form.instance = self.object
        commissions_form.save()

      # save deliveries
      for del_form in delivery_form:
        if del_form.has_changed() and del_form.instance.pk and not utils.delivery_form_empty(del_form.cleaned_data):
          del_form.instance = self.object
          del_form.save()
      return HttpResponseRedirect(self.get_success_url())
    else:
      return self.form_invalid(**kwargs)


  def form_invalid(self, *args, **kwargs):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the data")
    context = self.get_context_data()
    context.update(kwargs)

    return self.render_to_response(context)

  def get_context_data(self, **kwargs):
    context = super(OrderUpdateView, self).get_context_data(**kwargs)
    context['item_form_helper'] = OrderItemFormHelper
    return context

  def get_success_url(self):
    return self.get_object().get_absolute_url() #reverse('order_detail', kwargs={'pk': self.object.pk})

class OrderCreateView(PermissionRequiredMixin, CreateView):
  model = Order
  template_name = "orders/order_update.html"
  form_class = OrderForm

  required_permissions = (
    'orders.add_order',
  )

  def get(self, request, *args, **kwargs):
    """ 
    Handle GET requests and instantiate blank version of the form
    and it's inline formsets
    """
    self.object = None 
    form_class = self.get_form_class()
    form = self.get_form(form_class)

    # initialize form defaults
    form.fields['status'].widget.attrs['readonly'] = True

    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers")
    items_form = ItemFormSet(prefix="ordered_items")
    commissions_form = CommissionFormSet(prefix="commissions")
    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
    }
    context = self.get_context_data()
    context.update(extra_forms)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """
    self.object = None
    form_class = self.get_form_class()
    form = self.get_form(form_class)

    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")
    items_form = ItemFormSet(self.request.POST, self.request.FILES, prefix="ordered_items")
    commissions_form = CommissionFormSet(self.request.POST, self.request.FILES, prefix="commissions")
    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
    }

    if form.is_valid() and items_form.is_valid() and commissions_form.is_valid(): 
      return self.form_valid(**forms)
    else:
      return self.form_invalid(**forms)

  def form_invalid(self, *args, **kwargs): 
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving order form information")
    context = self.get_context_data(messages=messages)
    context.update(kwargs)
    return self.render_to_response(context)

  def form_valid(self, *args, **kwargs):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    form = kwargs['form']
    customer_form = kwargs['customer_form']
    items_form = kwargs['items_form']
    commissions_form = kwargs['commissions_form']

    self.object = form.save(commit=False)
    
    # flags
    BR_passed = True
    new_customer=False

    # import pdb; pdb.set_trace()

    if not form.data['status'] or form.data['status'] not in ('Q', 'N'):
      messages.error(self.request, "Newly created order status must be either 'New' or 'Pending'!")
      BR_passed = False

    # validate customer
    if BR_passed:
      if form.cleaned_data['customer'] is None:
        if customer_form.is_valid():
          # check that first and last name are filled
          try:
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, "Please select existing customer or fill in new customer information!")
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, "Please select existing customer or fill in new customer information!")
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer form information!")
          BR_passed = False
  
#    # validate items
#    if BR_passed: 
#      for ind in xrange(items_form.total_form_count()):
#        try:
#          if items_form.cleaned_data[ind]['description'] is None:
#            BR_passed = False
#        except KeyError:
#          BR_passed = False
#
#      if not BR_passed:
#        messages.error(self.request, "Please enter sold item(s) description")

    if BR_passed: 
      
      #save order
      self.object.save()
      
      # save customer
      if new_customer:
          cust = customer_form[0].save()
          self.object.customer = cust

      # save items
      items_form.instance = self.object
      items_form.save()

      # save commissions
      commissions_form.instance = self.object
      commissions_form.save()

      return HttpResponseRedirect(self.get_success_url())
    else:
      return self.form_invalid(**kwargs)

  def get_context_data(self, **kwargs):
    context = super(OrderCreateView, self).get_context_data(**kwargs)
    context['item_form_helper'] = OrderItemFormHelper
    return context

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

  required_permissions = (
    'orders.delete_order',
  )

class FilteredTableMixin(object):
  formhelper_class = FormHelper
  context_filter_name = 'filter'
  context_table_name = 'table'
  model = None
  table_class = OrderTable
  context_object_name = "order_list"
  table_paginate_by = None 
  filter_class = OrderFilter
  filter_form_id = 'order-filter'

  def get_queryset(self, **kwargs):
    qs = super(FilteredTableMixin, self).get_queryset(**kwargs)
    self.setup_filter(queryset=qs)
    return self.filter.qs

  def setup_filter(self, **kwargs):
    self.filter = self.filter_class(self.request.GET, queryset=kwargs['queryset'])
    #self.filter.helper = self.formhelper_class()
    self.filter.helper.form_id = self.filter_form_id
    #self.filter.helper.form_class = "blueForms, well"
    self.filter.helper.form_method = "get"
    #self.filter.helper.add_input(Submit('submit', 'Submit'))

  def get_table(self, **kwargs):
    try:
      page = self.kwargs['page']
    except KeyError:
      page = 1 
    options = {'paginate':{'page':page, 'per_page':self.table_paginate_by}}
    table_class = self.table_class
    table = table_class(**kwargs)
    RequestConfig(self.request, **options).configure(table)
    return table

  def get_context_data(self, **kwargs):
    context = super(FilteredTableMixin, self).get_context_data(**kwargs)
    table = self.get_table(data=context[self.context_object_name])
    context[self.context_table_name] = table
    context[self.context_filter_name] = self.filter
    return context

class OrderMonthArchiveTableView(PermissionRequiredMixin, FilteredTableMixin, MonthArchiveView):
  model = Order
  table_paginate_by = 20 

  # archive view specific fields
  date_field = "created"
  make_object_list = True
  allow_future = False
  allow_empty = True
  template_name = "orders/order_archive_month.html"
  month_format = '%b'

  required_permissions = (
    'orders.view_orders',
  )

  def get_context_data(self, **kwargs):
    unfiltered_orders = self.get_month_dated_queryset() 
    context = super(OrderMonthArchiveTableView, self).get_context_data(**kwargs)

    # get monthly sales totals
    month_totals_table = self._get_sales_totals(unfiltered_orders)
    RequestConfig(self.request).configure(month_totals_table)
    context['month_totals_table'] = month_totals_table

    #calc YTD stats
    year = self.get_year()
    date_field = self.get_date_field()
    date = datetime.strptime(str(year), self.get_year_format()).date()
    since = self._make_date_lookup_arg(date)
    until = self._make_date_lookup_arg(self._get_next_year(date))
    lookup_kwargs = {
        '%s__gte' % date_field: since,
        '%s__lt' % date_field: until,
    }
    ytd_orders = self.model._default_manager.filter(**lookup_kwargs)
    ytd_totals_table =  self._get_sales_totals(ytd_orders)
    RequestConfig(self.request).configure(ytd_totals_table)
    context['ytd_totals_table'] = ytd_totals_table

    #calc sales totals by associate
    sales_by_assoc_data = order_utils._calc_sales_assoc_by_orders(unfiltered_orders)
    sales_by_assoc = SalesByAssociateTable(sales_by_assoc_data)
    RequestConfig(self.request).configure(sales_by_assoc)
    context['sales_by_associate'] = sales_by_assoc 

    #links to other months data
    context['order_months_links'] = self._get_month_list_for_year()
    context['previous_year_links'] = self._get_month_list_for_year(datetime.now().year-1)
    context['prev_year'] = datetime.now().year-1

    #unplaced orders
    unplaced_orders = Order.objects.unplaced_orders()
    unplaced_orders_table = OrderTable(unplaced_orders)
    RequestConfig(self.request).configure(unplaced_orders_table)
    context['unplaced_orders_table'] = unplaced_orders_table

    return context

  def _get_month_list_for_year(self, year=datetime.now().year):
    cur_date = datetime(year, 1, 1)
    months_data = []
    while cur_date.year == year:
      months_data.append((cur_date.strftime("%m"), cur_date.strftime("%b")))
      cur_date = cur_date + timedelta(days=31)
      cur_date = datetime(cur_date.year, cur_date.month, 1)
      if cur_date > datetime.now():
        break
    return [(name, reverse('archive_month_numeric', kwargs={'year':year, 'month':m})) for m,name in sorted(months_data)]


  def _get_sales_totals(self, qs):
    totals_data = []
    if qs.count():
      subtotal_hq = sum([o.subtotal_after_discount for o in qs if o.store.name == "Sacramento"])
      subtotal_fnt = sum([o.subtotal_after_discount for o in qs if o.store.name == "Roseville"])
      total_hq = sum([o.grand_total for o in qs if o.store.name == "Sacramento"])
      total_fnt = sum([o.grand_total for o in qs if o.store.name == "Roseville"])
      totals_data = [
        {'item':'Subtotal After Discount', 'hq':utils.dollars(subtotal_hq), 'fnt':utils.dollars(subtotal_fnt), 'total':utils.dollars(subtotal_hq + subtotal_fnt)},
        {'item':'Grand Total', 'hq':utils.dollars(total_hq), 'fnt':utils.dollars(total_fnt), 'total':utils.dollars(total_hq + total_fnt)},
        ]
    totals_table = SalesTotalsTable(totals_data)
    return totals_table
  
  def get_month_dated_queryset(self):
    year = self.get_year()
    month = self.get_month()
    date_field = self.get_date_field()
    date = datetime.strptime("-".join((year, month)), "-".join((self.get_year_format(), self.get_month_format()))).date()
    since = self._make_date_lookup_arg(date)
    until = self._make_date_lookup_arg(self._get_next_month(date))
    lookup_kwargs = {
        '%s__gte' % date_field: since,
        '%s__lt' % date_field: until,
    }
    qs = self.model._default_manager.all().filter(**lookup_kwargs)
        
    return qs



class MyOrderListView(PermissionRequiredMixin, FilteredTableMixin, ListView):
  model = Order
  context_object_name = "order_list"
  template_name = "orders/order_filtered_table.html"
  table_paginate_by = 20 
 
  required_permissions = (
    'orders.view_orders',
  )

  def get_queryset(self, **kwargs):
    me = self.request.user
    qs = Order.objects.select_related().filter(commission__associate=me).all()
    self.setup_filter(queryset=qs)
    return self.filter.qs

class OrderWeekArchiveTableView(PermissionRequiredMixin, FilteredTableMixin, WeekArchiveView):
  model = Order
  table_paginate_by = 20 

  # archive view specific fields
  date_field = "created"
  make_object_list = True
  allow_future = True
  allow_empty = True
  template_name = "orders/order_archive_week.html"
  week_format = '%W'

  required_permissions = (
    'orders.view_orders',
  )

  def get(self, request, *args, **kwargs):
    self.date_list, self.object_list, extra_content = self.get_dated_items()
    context = self.get_context_data(object_list=self.object_list, date_list=self.date_list)
    context.update(extra_content)
    
    # extra fields for cur. week, prev, and next week
    extra = {
      'next_week_num': context['next_week'].isocalendar()[1] - 1,
      'prev_week_num': context['previous_week'].isocalendar()[1] - 1,
      'next_week_sun': context['next_week'] + timedelta(days=7),
      'this_week_sun': context['week'] + timedelta(days=6),
    }
    context.update(extra)

    return self.render_to_response(context)

class DeliveriesTableView(LoginRequiredMixin, SingleTableView):
  model = OrderDelivery
  table_class = DeliveriesTable
  context_table_name = 'table' 
  template_name = "orders/delivery_list.html"
  paginate_by = 20 

class DeliveryDetailView(LoginRequiredMixin, DetailView):
  model = OrderDelivery
  context_object_name = "delivery"
  template_name = "orders/delivery_detail.html"

class DeliveryDeleteView(LoginRequiredMixin, DeleteView):
  model = OrderDelivery
  success_url = reverse_lazy("delivery_list")

class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
  model = OrderDelivery
  context_object_name = "delivery"
  template_name = "orders/delivery_update.html"
  form_class = OrderDeliveryForm

  def get_form_kwargs(self):
    kwargs = super(DeliveryUpdateView, self).get_form_kwargs()
    kwargs.update({'request':self.request})
    return kwargs

class SalesStandingsMonthTableView(PermissionRequiredMixin, MonthArchiveView):
  # archive view specific fields
  date_field = "created"
  make_object_list = True
  allow_future = True
  allow_empty = True
  template_name = "orders/commissions_monthly.html"
  month_format = '%b'
  queryset = Order.objects.all()

  required_permissions = (
    'orders.view_sales',
  )

  def get_context_data(self, **kwargs):
    context = super(SalesStandingsMonthTableView, self).get_context_data(**kwargs)

    orders = context['object_list']
    sales_by_assoc_data = order_utils._calc_sales_assoc_by_orders(orders)
    sales_by_assoc = SalesByAssociateTable(sales_by_assoc_data)

    RequestConfig(self.request).configure(sales_by_assoc)
    context['sales_by_associate'] = sales_by_assoc 

    sales_by_assoc_data_ytd = order_utils._calc_sales_assoc_by_orders(self.queryset)
    sales_by_assoc_ytd = SalesByAssociateTable(sales_by_assoc_data_ytd)
    RequestConfig(self.request).configure(sales_by_assoc_ytd)
    context['sales_by_associate_ytd'] = sales_by_assoc_ytd 

    return context

class HomePageRedirectView(LoginRequiredMixin, RedirectView):
  url = reverse_lazy('order_list')

  def get_redirect_url(self, **kwargs):
    # redirect directly to deliveries page if user belongs to group delivery_person
    if utils.is_user_delivery_group(self.request):
      self.url = reverse('delivery_list')

    return super(HomePageRedirectView, self).get_redirect_url(**kwargs)
