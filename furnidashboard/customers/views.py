from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from orders.forms import CustomerForm, CustomerDetailReadOnlyForm
from customers.models import Customer

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
  model = Customer
  context_object_name = "customer"
  template_name = "customers/customer_update.html"
  form_class = CustomerForm

class CustomerCreateView(LoginRequiredMixin, CreateView):
  model = Customer
  context_object_name = "customer"
  template_name = "customers/customer_update.html"
  form_class = CustomerForm

class CustomerDetailView(LoginRequiredMixin, DetailView):
  model = Customer
  context_object_name = "customer"
  template_name = "customers/customer_detail.html"
  
  def get_context_data(self, **kwargs):
    context = super(CustomerDetailView, self).get_context_data(**kwargs)
    context['customer_details_form'] = CustomerDetailReadOnlyForm(instance = context['object'])
    return context
