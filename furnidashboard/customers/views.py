from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView
import django_tables2 as tables
from django_tables2 import SingleTableView
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from orders.forms import CustomerForm, CustomerDetailReadOnlyForm
from customers.models import Customer
from .tables import CustomersTable

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

class CustomerTableView(LoginRequiredMixin, SingleTableView):
  model = Customer
  table_class = CustomersTable
  template_name = "customers/customer_table.html"

