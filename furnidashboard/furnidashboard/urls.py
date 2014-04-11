from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from orders.models import Order
from customers.models import Customer
from orders.views import UnplacedOrderTableView, MyOrderListView, OrderUpdateView, OrderDetailView, OrderCreateView, OrderDeleteView, OrderWeekArchiveView, OrderMonthArchiveTableView, DeliveriesTableView
from customers.views import CustomerCreateView, CustomerUpdateView, CustomerDetailView
from django.views.generic.edit import FormView
from orders.forms import OrderForm
from datetime import date

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

this_month_args = {'year':str(date.today().year), 'month':str(date.today().month)}

urlpatterns = patterns('',
    
    #home page template
    url(
      regex=r'^$',
      view=OrderMonthArchiveTableView.as_view(month_format='%m', **this_month_args),
      name="home",
    ),
    # url(r'^$', TemplateView.as_view(template_name='base.html')),  
    # url(r'^$', FormView.as_view(form_class=OrderForm, template_name = 'orders/form.html')),    
    
    url(
        regex= r'^orders/$', 
        # view=OrderListView.as_view(),
        view=OrderMonthArchiveTableView.as_view(year=str(date.today().year), month=str(date.today().month), month_format='%m'),
        name="order_list",
    ),
    url(
        regex= r'^orders/unplaced/$', 
        view=UnplacedOrderTableView.as_view(),
        name="unplaced_orders",
    ),
    url(
        regex= r'^my-orders/$', 
        view=MyOrderListView.as_view(),
        name="my_order_list",
    ),
    url(
        regex = r'^orders/(?P<pk>\d+)/$', 
        view=OrderDetailView.as_view(),
        name="order_detail",
    ),
    url(
        regex = r'^orders/(?P<pk>\d+)/edit/$', 
        view=login_required(OrderUpdateView.as_view()),
        name="order_edit",
    ),
    url(
        regex = r'^orders/(?P<pk>\d+)/delete/$', 
        view=login_required(OrderDeleteView.as_view()),
        name="order_delete",
    ),
    url(r'orders/add/$', login_required(OrderCreateView.as_view()), name="order_add"),
    url(r'orders/(?P<pk>\d+)/delete/$', login_required(OrderDeleteView.as_view()), name="order_delete"),

    # Archive Views
    # Month:
    url(
        # /2014/mar/
        regex = r'^orders/(?P<year>\d{4})/(?P<month>[a-zA-z]+)/$', 
        view=OrderMonthArchiveTableView.as_view(),
        name="archive_month",
    ),
    url(
        # /2014/03/
        regex = r'^orders/(?P<year>\d{4})/(?P<month>\d+)/$', 
        view=OrderMonthArchiveTableView.as_view(month_format='%m'),
        name="archive_month_numeric",
    ),
    url(
        # /this-month
        regex = r'^orders/this-month/$', 
        view=OrderMonthArchiveTableView.as_view(year=str(date.today().year), month=str(date.today().month), month_format='%m'),
        name="archive_this_month",
    ),
    # Weekly
    url(
        # /this-week
        regex = r'^orders/this-week/$', 
        view=OrderWeekArchiveView.as_view(year=str(date.today().year), week=str(int(date.today().isocalendar()[1]) - 1)),
        name="archive_this_week",
    ),
    url(
        # /2014/week/01/
        regex = r'^orders/(?P<year>\d{4})/week/(?P<week>\d+)/$', 
        view=OrderWeekArchiveView.as_view(),
        name="archive_week",
    ),

    # Customer links
    url(r'customers/$', login_required(ListView.as_view(model=Customer, template_name="customers/customer_list.html")), name="customer_list"),
    url(
        regex = r'^customers/(?P<pk>\d+)/edit/$', 
        view=CustomerUpdateView.as_view(),
        name="customer_edit",
    ),
    url(
        regex = r'^customers/add/$', 
        view=CustomerCreateView.as_view(),
        name="customer_add",
    ),
    url(
        regex = r'^customers/(?P<pk>\d+)/$', 
        view=CustomerDetailView.as_view(),
        name="customer_detail",
    ),

    # authentication-related URLs
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    # search
    url(
        regex = r'^search/$',
        view = 'core.views.search',
        name = "search",
    ),

    # deliveries
    url(
        regex = r'^deliveries/$',
        view = DeliveriesTableView.as_view() ,
        name = "search",
    ),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # administration URLs 
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ajax_select/', include('ajax_select.urls')),
)
