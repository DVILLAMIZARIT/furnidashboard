from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView
import django_tables2 as tables
from django_tables2 import RequestConfig, SingleTableView
from core.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from orders.forms import CustomerForm, CustomerDetailReadOnlyForm
from orders.tables import OrderTable
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

    customer_orders = context['object'].order_set.all()
    customer_orders_table = OrderTable(customer_orders)
    RequestConfig(self.request).configure(customer_orders_table)
    context['customer_orders_table'] = customer_orders_table
    return context

class CustomerTableView(LoginRequiredMixin, SingleTableView):
  model = Customer
  table_class = CustomersTable
  template_name = "customers/customer_table.html"
