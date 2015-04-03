from django.views.generic import ListView, DetailView, UpdateView, RedirectView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView, WeekArchiveView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django_tables2 import RequestConfig, SingleTableView
from django.db.models import Q
from datetime import timedelta, date, datetime
from .models import Order, OrderItem, OrderDelivery, OrderIssue
from .tables import OrderTable, UnplacedOrdersTable, SalesByAssociateTable, SalesByAssociateWithBonusTable, DeliveriesTable, SalesTotalsTable,SalesByAssocSalesTable
from .forms import OrderForm, CustomerFormSet, CommissionFormSet, ItemFormSet, get_ordered_items_formset, DeliveryFormSet, get_deliveries_formset, get_commissions_formset, OrderDeliveryForm, OrderItemFormHelper, OrderAttachmentFormSet, get_order_issues_formset
import orders.forms as order_forms
from .filters import OrderFilter
from customers.models import Customer
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import core.utils as utils
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin
import orders.utils as order_utils
import json

class OrderDetailView(PermissionRequiredMixin, DetailView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_detail.html"

  required_permissions = (
    'orders.view_orders',
  )

  def get_context_data(self, **kwargs):
    context = super(OrderDetailView, self).get_context_data(**kwargs)
    user_model = get_user_model()
    return context

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

    # attachments
    attachment_form = OrderAttachmentFormSet(instance=self.object, prefix="attachments")

    # issues form
    OrderIssuesFormSet = get_order_issues_formset()
    issues_form = OrderIssuesFormSet(instance=self.object, prefix='issues')


    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
      'attachment_form':attachment_form,
      'issues_form':issues_form,
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
    
    if not request.user.has_perm('orders.update_status'):
      #disable order status for staff person without privilege
      form.fields['status'].widget.attrs['readonly'] = 'readonly'

    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")

    #commissions_form = CommissionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="commissions")
    extra = 1 if self.object.commission_set.count() == 0 else 0  #if no commissions were saved for this order, add a blank form
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="commissions")

    items_form = ItemFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="ordered_items")
    DeliveriesFormSet = get_deliveries_formset(extra=0, max_num=100, request=self.request)
    delivery_form = DeliveriesFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="deliveries")

    attachment_form = OrderAttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="attachments")

    OrderIssuesFormSet = get_order_issues_formset()
    issues_form = OrderIssuesFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="issues")

    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
      'attachment_form':attachment_form,
      'issues_form': issues_form,
    }

    #check if forms are valid
    forms_valid = form.is_valid()
    if forms_valid and commissions_form.has_changed():
      forms_valid = commissions_form.is_valid()
    if forms_valid and items_form.has_changed():  
      forms_valid = items_form.is_valid()
    if forms_valid :
      for form in [f for f in delivery_form.forms if f.has_changed()]: # and  f not in delivery_form.deleted_forms]:  
        forms_valid = form.is_valid()
        if not forms_valid:
          break
    if forms_valid and attachment_form.has_changed():  
      forms_valid = attachment_form.is_valid()
      
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
    attachment_form = kwargs['attachment_form']
    issues_form = kwargs.get('issues_form')
    
    orig_status = self.object.status
    self.object = form.save(commit=False)

    # flags
    BR_passed = True
    new_customer=False

    # import pdb; pdb.set_trace()

    # validate order status
    if not form.data['status'] :
      messages.error(self.request, "Order status cannot be blank!", extra_tags="alert")
      BR_passed = False
    else:
      new_status = form.cleaned_data['status']
      if new_status == 'C' and any([comm_data['paid'] == False for comm_data in commissions_form.cleaned_data]): 
        messages.add_message(self.request, messages.ERROR, "Cannot close the order while there are unpaid commissions due!", extra_tags="alert alert-danger")
        BR_passed = False
      elif new_status == 'D' and not [f for f in delivery_form if not utils.delivery_form_empty(f.cleaned_data)]:
        messages.add_message(self.request, messages.ERROR, "Cannot set order status to 'Delivered' because there are no deliveries recorded for this order.", extra_tags="alert alert-danger")
        BR_passed = False
      elif new_status == 'X' and any([i for i in items_form.cleaned_data if i['in_stock'] == False]):
        messages.add_message(self.request, messages.ERROR, "Cannot set order status to 'Dummy' because there are special order items.", extra_tags="alert alert-danger")
        BR_passed = False


    # validate customer
    if BR_passed:
      if self.object.customer is None:
        if customer_form.is_valid():
          # check that first and last name are filled
          try:
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, "Please select existing customer or fill in new customer information!", extra_tags="alert alert-danger")
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, "Please select existing customer or fill in new customer information!", extra_tags="alert alert-danger")
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer information!", extra_tags="alert alert-danger")
          BR_passed = False

    # validate issues
    if BR_passed and not issues_form.is_valid():
      messages.error(self.request, "Error saving 'order issues' information!", extra_tags="alert alert-danger")
      BR_passed = False
  

    # Final check
    if BR_passed: 
      
      if not self.request.user.has_perm('orders.update_status'):
        if orig_status:
          self.object.status = orig_status #reset previous value
          messages.warning(self.request, "You don't have permission to change order status. Order status was reset to previous value.", extra_tags="alert")
        
      
      # save customer
      if new_customer:
        cust = customer_form[0].save()
        self.object.customer = cust

      #save order
      self.object.save()

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
        if del_form.has_changed():
          if del_form.instance.pk or not utils.delivery_form_empty(del_form.cleaned_data):
            del_form.order = self.object
            del_form.save()
            if any(self.object.orderitem_set.filter(~Q(status__in=['S', 'R']))):
              messages.add_message(self.request, messages.ERROR, "Warning: a delivery has been scheduled for this order BUT item(s) are not in stock/not delivered. Please check the order status for any issues.", extra_tags="alert")

      # save attachments
      if attachment_form.has_changed():
        attachment_form.instance = self.object
        attachment_form.save()

      # save issues
      if issues_form.has_changed():
        issues_form.instance = self.object
        issues_form.save()

      return HttpResponseRedirect(self.get_success_url())
    else:
      return self.form_invalid(**kwargs)


  def form_invalid(self, *args, **kwargs):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.add_message(self.request, messages.ERROR, "Error updating the order. Please go through tabs to fix the invalid information.", extra_tags="alert alert-danger")
    context = self.get_context_data()
    context.update(kwargs)

    return self.render_to_response(context)

  def get_context_data(self, **kwargs):
    context = super(OrderUpdateView, self).get_context_data(**kwargs)
    context['item_form_helper'] = OrderItemFormHelper
    return context

  def get_success_url(self):
    return self.get_object().get_absolute_url() #reverse('order_detail', kwargs={'pk': self.object.pk})



#------------------------------------------------------------------------

class OrderCreateView(PermissionRequiredMixin, CreateView):
  """
  Order Creation view. Presents blank forms for inputting new orders.
  """

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

    extra = 1 
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(prefix="commissions")

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

    # initialize form defaults
    form.fields['status'].widget.attrs['readonly'] = True

    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")
    items_form = ItemFormSet(self.request.POST, self.request.FILES, prefix="ordered_items")

    SpecialCommissionFormSet = get_commissions_formset(extra=1, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(self.request.POST, self.request.FILES, prefix="commissions")

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
    error_tag = "alert alert-danger"
    # messages.error(self.request, "Error saving order form information", extra_tags=error_tag)
    messages.add_message(self.request, messages.ERROR, "Error saving the order information. Please go through tabs to fix invalid information.", extra_tags="alert alert-danger")
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
    
    error_tag = "alert alert-danger"

    # flags
    BR_passed = True
    new_customer=False

    if not form.data['status'] or form.data['status'] not in ('Q', 'N', 'X'):
      messages.error(self.request, "Newly created order status must be either 'New', 'Pending', or 'Dummy'!", extra_tags=error_tag)
      BR_passed = False

    # validate customer
    if BR_passed:

      if self.object.customer is None:
        if customer_form.has_changed() and customer_form.is_valid():
          try:
            # check that first and last name are filled
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, "Please select existing customer or fill in new customer information!", extra_tags=error_tag)
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, "Please select existing customer or fill in new customer information!", extra_tags=error_tag)
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer form information!", extra_tags=error_tag)
          BR_passed = False
  

    if BR_passed: 
      
      # save customer
      if new_customer:
        cust = customer_form[0].save()
        self.object.customer = cust

      #save order
      self.object.save()

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

#-----------------------------------------------------------------------

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
  table_paginate_by = 50 

  # archive view specific fields
  date_field = "order_date"
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
    month_totals_table = _get_sales_totals(unfiltered_orders)
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
    ytd_totals_table =  _get_sales_totals(ytd_orders)
    RequestConfig(self.request).configure(ytd_totals_table)
    context['ytd_totals_table'] = ytd_totals_table

    #calc sales totals by associate
    sales_by_assoc_data, tmp = order_utils._calc_sales_assoc_by_orders(unfiltered_orders)
    sales_by_assoc = SalesByAssociateTable(sales_by_assoc_data)
    RequestConfig(self.request).configure(sales_by_assoc)
    context['sales_by_associate'] = sales_by_assoc 

    #links to other months data
    context['order_months_links'] = self._get_month_list_for_year()
    context['previous_year_links'] = self._get_month_list_for_year(datetime.now().year-1)
    context['prev_year'] = datetime.now().year-1

    context['months_2013'] = self._get_month_list_for_year(datetime.now().year-2)

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


class ActiveOrdersTableView(PermissionRequiredMixin, FilteredTableMixin, ListView):
  model = Order
  table_paginate_by = 50 
  context_object_name = 'order_list'
  template_name = "orders/order_filtered_list.html"
  required_permissions = (
    'orders.view_orders',
  )
  queryset = Order.objects.open_orders()

  def get_context_data(self, **kwargs):
    context = super(ActiveOrdersTableView, self).get_context_data(**kwargs)
    table = self.get_table(data=context[self.context_object_name])
    context[self.context_table_name] = table
    context[self.context_filter_name] = self.filter
    context['list_label'] = 'All Active Orders'
    return context

class MyOrderListView(PermissionRequiredMixin, FilteredTableMixin, ListView):
  model = Order
  context_object_name = "order_list"
  #template_name = "orders/order_filtered_table.html"
  template_name = "orders/order_filtered_list.html"
  table_paginate_by = 50 
 
  required_permissions = (
    'orders.view_orders',
  )

  def get_queryset(self, **kwargs):
    me = self.request.user
    qs = Order.objects.select_related().filter(commission__associate=me).all()
    self.setup_filter(queryset=qs)
    return self.filter.qs

  def get_context_data(self, **kwargs):
    context = super(MyOrderListView, self).get_context_data(**kwargs)
    context['list_label'] = 'Just my orders'
    return context

class OrderWeekArchiveTableView(PermissionRequiredMixin, FilteredTableMixin, WeekArchiveView):
  model = Order
  table_paginate_by = 50 

  # archive view specific fields
  date_field = "order_date"
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

  def get_queryset(self, **kwargs):
    return OrderDelivery.objects.filter(~Q(delivery_type='SELF'))

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

class SalesStandingsMonthTableView(PermissionRequiredMixin, ListView):
  model = Order
  context_object_name = "order_list"
  template_name = "orders/commissions_monthly.html"
  from_date = ""
  to_date = ""

  required_permissions = (
    'orders.view_sales',
  )
  
  def get_queryset(self, **kwargs):
    #qs = super(FilteredTableMixin, self).get_queryset(**kwargs)
    date_range = ""
    try:
      date_range = self.request.GET['date_range']
    except KeyError, e:
      pass
    
    self.from_date, self.to_date = order_utils.get_date_range(date_range, self.request);   
    
    qs = Order.objects.get_dated_qs(self.from_date, self.to_date)
    
    return qs

  def get_context_data(self, **kwargs):
    context = super(SalesStandingsMonthTableView, self).get_context_data(**kwargs)

    context['date_range_filter'] = order_forms.SalesReportForm(self.request.GET)
    
    date_range = ""
    if self.request.GET.has_key("date_range"):
      date_range = self.request.GET['date_range']
    context['dates_caption'] = "{0} - {1}".format(self.from_date.strftime("%Y-%m-%d"), self.to_date.strftime("%Y-%m-%d"))

    orders = context[self.context_object_name]
    sales_by_assoc_data, sales_by_assoc_expanded_data = order_utils._calc_sales_assoc_by_orders(orders)

    #total sales table
    sales_by_assoc_table = SalesByAssociateTable(sales_by_assoc_data)
    RequestConfig(self.request).configure(sales_by_assoc_table)
    context['sales_by_associate'] = sales_by_assoc_table 
    
    #prepare expanded tables per each associate
    sales_by_assoc_expanded_tables= {}
    count = 1
    for assoc, sales in sales_by_assoc_expanded_data.items():
      sales_by_assoc_expanded_tables[assoc] = SalesByAssocSalesTable(sales, prefix="tbl"+ str(count)) 
      RequestConfig(self.request).configure(sales_by_assoc_expanded_tables[assoc])
      count += 1
    context['sales_by_assoc_expanded_tables'] = sales_by_assoc_expanded_tables

    #sales by stores table 
    store_totals_table =  _get_sales_totals(orders)
    RequestConfig(self.request).configure(store_totals_table)
    context['store_totals_table'] = store_totals_table

    # sales_by_assoc_data_ytd = order_utils._calc_sales_assoc_by_orders(self.queryset)
    # sales_by_assoc_ytd = SalesByAssociateTable(sales_by_assoc_data_ytd)
    # RequestConfig(self.request).configure(sales_by_assoc_ytd)
    # context['sales_by_associate_ytd'] = sales_by_assoc_ytd 
    
    #context['sales_data_ytd_raw'] = json.dumps([{'key':data['associate'], 'value':data['sales']} for data in sales_by_assoc_data])

    return context

class HomePageRedirectView(LoginRequiredMixin, RedirectView):
  url = reverse_lazy('order_list')

  def get_redirect_url(self, **kwargs):
    # redirect directly to deliveries page if user belongs to group delivery_person
    if utils.is_user_delivery_group(self.request):
      self.url = reverse('delivery_list')

    return super(HomePageRedirectView, self).get_redirect_url(**kwargs)

def _get_sales_totals(qs):
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
