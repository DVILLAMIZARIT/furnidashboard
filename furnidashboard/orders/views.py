from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView, WeekArchiveView
from .models import Order, OrderItem, OrderDelivery
from .tables import OrderTable, UnplacedOrdersTable, SalesByAssociateTable
from .forms import OrderForm, CustomerFormSet, CommissionFormSet, ItemFormSet, get_ordered_items_formset, DeliveryFormSet, get_deliveries_formset, get_commissions_formset
from customers.models import Customer
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig, SingleTableView
from django.db.models import Q
from datetime import timedelta, date, datetime
import django_filters as filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class OrderFilter(filters.FilterSet):
  class Meta:
    model = Order
    fields = ['store', 'status', 'commission__associate']

#class PagedFilteredTableView(SingleTableView):
#  filter_class = None
#  formhelper_class = None
#  context_filter_name = 'filter'
#
#  def get_queryset(self, **kwargs):
#    qs = super(PagedFilteredTableView, self).get_queryset(**kwargs)
#    self.filter = self.filter_class(self.request.GET, queryset=qs)
#    # self.filter.form.helper = self.formhelper_class()
#    return self.filter.qs
#
#  def get_table(self, **kwargs):
#    table = super(PagedFilteredTableView, self).get_table()
#    try:
#      page = self.kwargs['page']
#    except KeyError:
#      page = 1 
#    RequestConfig(self.request, paginate={'page':page,
#                      'per_page':self.paginate_by}).configure(table)
#    return table
#
#  def get_context_data(self, **kwargs):
#    context = super(PagedFilteredTableView, self).get_context_data(**kwargs)
#    context[self.context_filter_name] = self.filter
#    return context

class UnplacedOrderTableView(SingleTableView):
  model = Order
  table_class = OrderTable
  template_name = "orders/order_table.html"

  def get_queryset(self, **kwargs):
    return  Order.objects.select_related().filter(Q(status=None) | Q(status='N') | (Q(orderitem__in_stock=False) & (Q(orderitem__po_num__isnull=True) | Q(orderitem__po_num="")))).distinct()

#class OrderFilteredTableView(LoginRequiredMixin, PagedFilteredTableView):
#  model = Order
#  table_class = OrderTable
#  template_name = "orders/order_filtered_table.html"
#  context_object_name = "order_list"
#  paginate_by = 5
#  filter_class = OrderFilter
## formhelper_class = OrderFilterFormHelper

#class OrderListView(LoginRequiredMixin, ListView):
#  model = Order
#  context_object_name = "order_list"
#  template_name = "orders/order_list.html"
#
#  def get_queryset(self):
#    return Order.objects.select_related().all() # super(OrderListView, self).get_queryset().select_related()
#
#  def get_context_data(self, **kwargs):
#    context = super(OrderListView, self).get_context_data(**kwargs)
#    recent_orders_table = OrderTable(context['order_list'])
#    unplaced_orders = context['object_list'].filter(Q(status=None) | Q(status='N') | (Q(orderitem__in_stock=False) & (Q(orderitem__po_num__isnull=True) | Q(orderitem__po_num="")))).distinct()
#    unplaced_orders_table = UnplacedOrdersTable(unplaced_orders)
#
#    now = datetime.now()
#    sales_by_assoc_data = _calc_sales_by_assoc(now.year, now.month) #[{'associate':'Lana', 'sales':5000}, {'associate':'Pearl', 'sales':10000}]
#    sales_by_assoc = SalesByAssociateTable(sales_by_assoc_data)
#
#    RequestConfig(self.request).configure(recent_orders_table)
#    RequestConfig(self.request).configure(unplaced_orders_table)
#    RequestConfig(self.request).configure(sales_by_assoc)
#    context['recent_orders_table'] = recent_orders_table
#    context['unplaced_orders_table'] = unplaced_orders_table
#    context['sales_by_associate'] = sales_by_assoc 
#
#    return context

#class MyOrderListView(OrderListView, ListView):
#  def get_queryset(self):
#    me = self.request.user
#    return Order.objects.select_related().filter(commission__associate=me) # super(OrderListView, self).get_queryset().select_related()

class OrderDetailView(LoginRequiredMixin, DetailView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_detail.html"

class OrderDeleteView(LoginRequiredMixin, DeleteView):
  model = Order
  context_object_name = "order"
  success_url = reverse_lazy("order_list")


class OrderUpdateView(LoginRequiredMixin, UpdateView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_update.html"
  form_class = OrderForm

  def get(self, request, *args, **kwargs):
    """ 
    Handle GET requests and instantiate blank version of the form
    and it's inline formsets
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers") #filter(pk=self.object.customer_id))

    extra = 0
    if self.object.commission_set.count() == 0:
      extra = 1
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3)
    commission_form = SpecialCommissionFormSet(instance=self.object, prefix="commissions")
    
    DeliveriesFormSet = get_deliveries_formset(extra=1, max_num=100)
    delivery_form = DeliveriesFormSet(instance = self.object, prefix="deliveries")

    # prevent empty form showin up if no items were recorded for the order
    # specify at least 1 extra of no items are set
    # order_item_set = OrderItem.objects.filter(order=self.object)
    extra = 0
    if self.object.orderitem_set.count() == 0:
      extra = 1

    SoldItemsFormSet = get_ordered_items_formset(extra=extra, max_num=100)
    items_form = SoldItemsFormSet(instance=self.object, prefix="ordered_items")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form, items_form=items_form, delivery_form=delivery_form)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    #self.object = form.save(commit=False)
    customer_form = CustomerFormSet(self.request.POST, prefix="customers")
    commission_form = CommissionFormSet(self.request.POST, instance=self.object, prefix="commissions")
    items_form = ItemFormSet(self.request.POST, instance=self.object, prefix="ordered_items")
    delivery_form = DeliveryFormSet(self.request.POST, instance=self.object, prefix="deliveries")
    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commission_form':commission_form,
      'delivery_form':delivery_form,
    }
    if form.is_valid() and commission_form.is_valid() and items_form.is_valid() and delivery_form.is_valid():
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
    commission_form = kwargs['commission_form']
    delivery_form = kwargs['delivery_form']

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
  
    # validate items
    if BR_passed: 
      for ind in xrange(items_form.total_form_count()):
        try:
          if items_form.cleaned_data[ind]['description'] is None:
            BR_passed = False
        except KeyError:
          BR_passed = False

      if not BR_passed:
        messages.error(self.request, "Please enter sold item(s) description")

    if BR_passed: 
      
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
      if commission_form.has_changed():
        commission_form.instance = self.object
        commission_form.save()

      # save deliveries
      if delivery_form.has_changed():
        delivery_form.instance = self.object
        delivery_form.save()

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

  def get_success_url(self):
    return self.get_object().get_absolute_url() #reverse('order_detail', kwargs={'pk': self.object.pk})

class OrderCreateView(LoginRequiredMixin, CreateView):
  model = Order
  template_name = "orders/order_update.html"
  form_class = OrderForm

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
    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
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

    customer_form = CustomerFormSet(self.request.POST, prefix="customers")
    items_form = ItemFormSet(self.request.POST, prefix="ordered_items")

    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
    }

    if form.is_valid() and items_form.is_valid(): 
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

    self.object = form.save(commit=False)
    
    # flags
    BR_passed = True
    new_customer=False

    # import pdb; pdb.set_trace()

    if not form.data['status'] or form.data['status'] != 'N':
      messages.error(self.request, "New orders must have a status 'New'")
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
  
    # validate items
    if BR_passed: 
      for ind in xrange(items_form.total_form_count()):
        try:
          if items_form.cleaned_data[ind]['description'] is None:
            BR_passed = False
        except KeyError:
          BR_passed = False

      if not BR_passed:
        messages.error(self.request, "Please enter sold item(s) description")

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
      return HttpResponseRedirect(self.get_success_url())
    else:
      return self.form_invalid(**kwargs)

  def get_form(self, request=None, **kwargs):
    self.exclude = []
    #if not request.user.is_superuser:
    #  self.exclude.append(field_to_hide)
    
    #self.initial = {'status':'N'}

    return super(OrderCreateView, self).get_form(request, **kwargs)

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(LoginRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

#class OrderMonthArchiveView(LoginRequiredMixin, PagedFilteredTableView, MonthArchiveView):
#  queryset = Order.objects.all()
#  date_field = "created"
#  make_object_list = True
#  allow_future = True
#  template_name = "orders/order_archive_month.html"
#  month_format = '%b'


class OrderMonthArchiveTableView(LoginRequiredMixin, MonthArchiveView):
  # table-related fields
  formhelper_class = None
  context_filter_name = 'filter'
  context_table_name = 'table'
  model = Order
  table_class = OrderTable
  context_object_name = "order_list"
  paginate_by = 3 
  filter_class = OrderFilter

  # archive view specific fields
  # queryset = Order.objects.all()
  date_field = "created"
  make_object_list = True
  allow_future = True
  allow_empty = True
  template_name = "orders/order_archive_month.html"
  month_format = '%b'

  def get_queryset(self, **kwargs):
    qs = super(OrderMonthArchiveTableView, self).get_queryset(**kwargs)
    self.filter = self.filter_class(self.request.GET, queryset=qs)
    # self.filter.form.helper = self.formhelper_class()
    self.filter.helper = FormHelper()
    self.filter.helper.form_id = "order-list-monthly"
    self.filter.helper.form_class = "blueForms, hero-unit"
    self.filter.helper.form_method = "get"
    self.filter.helper.add_input(Submit('submit', 'Submit'))

    return self.filter.qs

  def get_table(self, **kwargs):
    try:
      page = self.kwargs['page']
    except KeyError:
      page = 1 
    options = {'paginate':{'page':page, 'per_page':self.paginate_by}}
    table_class = self.table_class
    table = table_class(**kwargs)
    RequestConfig(self.request, **options).configure(table)
    return table

  def get_context_data(self, **kwargs):
    context = super(OrderMonthArchiveTableView, self).get_context_data(**kwargs)
    table = self.get_table(data=context['order_list'])
    context[self.context_table_name] = table
    context[self.context_filter_name] = self.filter
    return context

class MyOrderListView(OrderMonthArchiveTableView):
  def get_queryset(self):
    me = self.request.user
    return Order.objects.select_related().filter(commission__associate=me) # super(OrderListView, self).get_queryset().select_related()

class OrderWeekArchiveView(LoginRequiredMixin, WeekArchiveView):
  queryset = Order.objects.all()
  date_field = "created"
  make_object_list = True
  allow_future = True
  allow_empty = True
  template_name = "orders/order_archive_week.html"
  week_format = '%W'

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

def _calc_sales_by_assoc(year, month):
  res = {}
  month_start = datetime(int(year), int(month), 1)
  month_end = month_start + timedelta(35)
  month_end = datetime(month_end.year, month_end.month, 1)
  orders = Order.objects.filter(Q(created__gte=month_start) & Q(created__lt=month_end))
  
  for o in orders:
    split_num = o.commission_set.count()
    comm_queryset = o.commission_set.select_related().all() 
    for com in comm_queryset:
      commission_amount = o.subtotal_after_discount / split_num
      if res.has_key(com.associate.first_name):
        res[com.associate.first_name] += commission_amount 
      else:
        res[com.associate.first_name] =  commission_amount
  
  sales_list = []
  for associate, amount in res.items():
    sales_list.append({'associate':associate, 'sales':amount })

  return sales_list
