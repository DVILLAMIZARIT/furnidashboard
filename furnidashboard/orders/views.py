from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView, WeekArchiveView
from .models import Order, OrderItem, OrderDelivery
from .tables import OrderTable, UnplacedOrdersTable
from .forms import OrderForm, CommissionFormSet, CustomerFormSet, ItemFormSet, get_ordered_items_formset, DeliveryFormSet, get_deliveries_formset
from customers.models import Customer
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig
from django.db.models import Q

class OrderListView(LoginRequiredMixin, ListView):
  model = Order
  context_object_name = "order_list"
  template_name = "orders/order_list.html"

  def dispatch(self, *args, **kwargs):
    return super(OrderListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(OrderListView, self).get_context_data(**kwargs)
    recent_orders_table = OrderTable(context['order_list'])
    unplaced_orders = context['object_list'].filter(Q(status=None) | Q(status='N') | (Q(orderitem__in_stock=False) & (Q(orderitem__po_num__isnull=True) | Q(orderitem__po_num="")))).distinct()
    unplaced_orders_table = UnplacedOrdersTable(unplaced_orders)
    RequestConfig(self.request).configure(recent_orders_table)
    RequestConfig(self.request).configure(unplaced_orders_table)
    context['recent_orders_table'] = recent_orders_table
    context['unplaced_orders_table'] = unplaced_orders_table
    return context

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
    commission_form = CommissionFormSet(instance=self.object, prefix="commissions")
    
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
    if form.is_valid() and commission_form.is_valid() and items_form.is_valid() and delivery_form.is_valid():
      return self.form_valid(form, commission_form, customer_form, items_form, delivery_form)
    else:
      return self.form_invalid(form, commission_form, customer_form, items_form, delivery_form)

  def form_valid(self, form, commission_form, customer_form, items_form, delivery_form):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    self.object = form.save(commit=False)

    if customer_form.has_changed():
      if customer_form.is_valid() and len(customer_form[0].cleaned_data['first_name'].strip()) > 0 and len(customer_form[0].cleaned_data['last_name'].strip()) > 0:
        cust = customer_form[0].save()
        self.object.customer = cust
      else:
        messages.error(self.request, "Please enter customer information")
        return self.form_invalid(form=form, commission_form=commission_form, customer_form=customer_form)

    #customer_form.instance = self.object
    #customer_form.save()
    self.object.save()
    commission_form.instance = self.object
    commission_form.save()
    items_form.instance = self.object
    items_form.save()
    delivery_form.instance = self.object
    delivery_form.save()

    return HttpResponseRedirect(self.get_success_url())

  def form_invalid(self, form, commission_form, customer_form, items_form, delivery_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the data")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form, items_form=items_form, delivery_form=delivery_form)

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
    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers")
    commission_form = CommissionFormSet(prefix="commissions")
    items_form = ItemFormSet(prefix="ordered_items")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form, items_form=items_form)
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
    commission_form = CommissionFormSet(self.request.POST, prefix="commissions")
    items_form = ItemFormSet(self.request.POST, prefix="ordered_items")
    if form.is_valid() and commission_form.is_valid() and items_form.is_valid(): 
      return self.form_valid(form, commission_form, customer_form, items_form)
    else:
      return self.form_invalid(form, commission_form, customer_form, items_form)

  def form_invalid(self, form, commission_form, customer_form, items_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the commissions information")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form, items_form=items_form, messages=messages)
    return self.render_to_response(context)

  def form_valid(self, form, commission_form, customer_form, items_form):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """

    self.object = form.save(commit=False)

    import pdb; pdb.set_trace()

    if form.cleaned_data['customer'] is None:
      if customer_form.is_valid():
        cust = customer_form[0].save()
        self.object.customer = cust
      else:
        return self.form_invald(form=form, commission_form=commission_form, customer_form=customer_form)
    
    #customer_form.instance = self.object
    #customer_form.save()
    self.object.save()
    commission_form.instance = self.object
    commission_form.save()
    items_form.instance = self.object
    items_form.save()
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(LoginRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

class OrderMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
  queryset = Order.objects.all()
  date_field = "created"
  make_object_list = True
  allow_future = True
  template_name = "orders/order_archive_month.html"
  month_format = '%b'

class OrderWeekArchiveView(LoginRequiredMixin, WeekArchiveView):
  queryset = Order.objects.all()
  date_field = "created"
  make_object_list = True
  allow_future = True
  template_name = "orders/order_archive_week.html"
  month_format = '%W'
