from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from .models import Order
from .tables import OrderTable
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
    table = OrderTable(context['order_list'])
    RequestConfig(self.request).configure(table)
    context['table'] = table
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
    #customer_form = CustomerFormSet(queryset=Customer.objects.filter(pk=self.object.customer.pk))
    commission_form = CommissionFormSet(instance=self.object)
    context = self.get_context_data(form=form, commission_form=commission_form)
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
    #customer_form = CustomerFormSet(self.request.POST)
    commission_form = CommissionFormSet(self.request.POST, instance=self.get_object())
    if form.is_valid() and commission_form.is_valid():
      return self.form_valid(form, commission_form)
    else:
      return self.form_invalid(form, commission_form)

  def form_valid(self, form, commission_form):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    form.save()
    #customer_form.instance = self.object
    #customer_form.save()
    commission_form.instance = self.get_object()
    commission_form.save()
    return HttpResponseRedirect(self.get_success_url())

  def form_invalid(self, form, commission_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the commissions information")
    context = self.get_context_data(form=form, commission_form=commission_form)
    return self.render_to_response(context)

#    if form.is_valid():
#      context = self.get_context_data(form=form)
#      commission_form = context['commission_formset']
#      customer_form = context['customer_formset'][0]
#      self.object = form.save()
#      if commission_form.is_valid():
#        commission_form.save()
#      else:
#        messages.error(self.request, "Error saving the order information")
#        return self.form_invalid(form)
#
#      if customer_form.is_valid():
#        customer = customer_form.save()
#        self.object.customer = customer
#      else:
#        messages.error(self.request, "Error saving the customer information")
#        return self.form_invalid(form)
#
#      return super(OrderUpdateView, self).form_valid(form)
#
#  def post(self, request, *args, **kwargs):
#    self.object = self.get_object()
#    form_class = self.get_form_class()
#    form = self.get_form(form_class)
#    if form.is_valid():
#      context = self.get_context_data(form=form)
#      commission_form = context['commission_formset']
#      #self.object = form.save()
#      if commission_form.is_valid():
#        commission_form.save()
#      else:
#        messages.error(self.request, "Error saving the order information")
#        return self.form_invalid(form)
#
#      return self.form_valid(form)
#
#    else:
#      return self.form_invalid(form)
#
#  def get_context_data(self, **kwargs):
#    context = super(OrderUpdateView, self).get_context_data(**kwargs)
#    if self.request.POST:
#      context['commission_formset'] = CommissionFormSet(self.request.POST, instance=self.object)
#      context['customer_formset'] = CustomerFormSet(self.request.POST)
#    else:
#      context['commission_formset'] = CommissionFormSet(instance=self.object)
#      context['customer_formset'] = CustomerFormSet(queryset=Customer.objects.filter(pk=self.object.customer.pk))
#
#    return context

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
    #customer_form = CustomerFormSet(queryset=Customer.objects.none())
    commission_form = CommissionFormSet()
    context = self.get_context_data(form=form, commission_form=commission_form)
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
    #customer_form = CustomerFormSet(self.request.POST)
    commission_form = CommissionFormSet(self.request.POST)
    if form.is_valid() and commission_form.is_valid():
      return self.form_valid(form, commission_form)
    else:
      return self.form_invalid(form, commission_form)

  def form_invalid(self, form, commission_form):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    messages.error(self.request, "Error saving the commissions information")
    context = self.get_context_data(form=form, commission_form=commission_form, messages=messages)
    return self.render_to_response(context)

  def form_valid(self, form, commission_form):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    self.object = form.save()
    #customer_form.instance = self.object
    #customer_form.save()
    commission_form.instance = self.object
    commission_form.save()
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})

#  def form_valid(self, form):
#    if form.is_valid():
#      context = self.get_context_data(form=form)
#      customer_form = context['customer_formset'][0]
#      self.object = form.save()
#      if customer_form.is_valid():
#        customer = customer_form.save()
#        customer.save()
#        self.object.customer = customer
#      else:
#        messages.error(self.request, "Error saving the customer information")
#        return self.form_invalid(form)
#
#      return super(OrderCreateView, self).form_valid(form)

#  def post(self, request, *args, **kwargs):
#    self.object = None #self.get_object()
#    form_class = self.get_form_class()
#    form = self.get_form(form_class)
#    if form.is_valid():
#      context = self.get_context_data(form=form)
#      customer_form = context['customer_formset']
#      #self.object = form.save()
#      if customer_form.is_valid():
#        customer = customer_form.save()
#        self.object = form.save()
#        object.customer = customer
#      else:
#        messages.error(self.request, "Error saving the customer information")
#        return self.form_invalid(form)
#
#      return self.form_valid(form)
#
#    else:
#      return self.form_invalid(form)
#
#  def get_context_data(self, **kwargs):
#    context = super(OrderCreateView, self).get_context_data(**kwargs)
#    if self.request.POST:
#      context['customer_formset'] = CustomerFormSet(self.request.POST)
#    else:
#      context['customer_formset'] = CustomerFormSet(queryset=Customer.objects.none())
#
#    return context

class OrderDeleteView(LoginRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

