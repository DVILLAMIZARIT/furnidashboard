from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from .models import Order
from .tables import OrderTable, UnplacedOrdersTable
from .forms import OrderForm, CommissionFormSet, CustomerFormSet
from customers.models import Customer
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig

class OrderListView(LoginRequiredMixin, ListView):
  model = Order
  context_object_name = "order_list"
  template_name = "orders/order_list.html"

  def dispatch(self, *args, **kwargs):
    return super(OrderListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(OrderListView, self).get_context_data(**kwargs)
    recent_orders_table = OrderTable(context['order_list'])
    unplaced_orders = Order.objects.filter(status__in=('SP', 'ST'), vendor_order_no=None)
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
    customer_form = CustomerFormSet(queryset=Customer.objects.none()) #filter(pk=self.object.customer_id))
    commission_form = CommissionFormSet(instance=self.object)
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form)
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
    customer_form = CustomerFormSet(self.request.POST)
    commission_form = CommissionFormSet(self.request.POST, instance=self.object)
    if form.is_valid() and commission_form.is_valid():
      return self.form_valid(form, commission_form, customer_form)
    else:
      return self.form_invalid(form, commission_form, customer_form)

  def form_valid(self, form, commission_form, customer_form):
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
    commission_form.instance = self.object
    commission_form.save()
    self.object.save()
    return HttpResponseRedirect(self.get_success_url())

  def form_invalid(self, form, commission_form, customer_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the data")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form)
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
    customer_form = CustomerFormSet(queryset=Customer.objects.none())
    commission_form = CommissionFormSet()
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """
    self.object = None
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    #self.object = form.save(commit=False)
    customer_form = CustomerFormSet(self.request.POST)
    commission_form = CommissionFormSet(self.request.POST)
    if form.is_valid() and commission_form.is_valid(): 
      return self.form_valid(form, commission_form, customer_form)
    else:
      return self.form_invalid(form, commission_form, customer_form)

  def form_invalid(self, form, commission_form, customer_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the commissions information")
    context = self.get_context_data(form=form, commission_form=commission_form, customer_form=customer_form, messages=messages)
    return self.render_to_response(context)

  def form_valid(self, form, commission_form, customer_form):
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
    commission_form.instance = self.object
    commission_form.save()
    self.object.save()
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(LoginRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

