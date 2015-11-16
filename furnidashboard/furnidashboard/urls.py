from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from orders.models import Order
from customers.models import Customer
from customers.views import CustomerCreateView, CustomerUpdateView, CustomerDetailView, CustomerTableView
#from orders.views import MyOrderListView, OrderUpdateView, OrderDetailView, OrderCreateView, OrderDeleteView, OrderMonthArchiveTableView, DeliveriesTableView, DeliveryDetailView, DeliveryUpdateView, DeliveryDeleteView, SalesStandingsMonthTableView, HomePageRedirectView, ActiveOrdersTableView
import orders.views.general as general_views
import orders.views.order_crud as order_crud_views
import orders.views.deliveries as deliveries_views
from commissions.views import BonusMonthlyReportView
import claims.views as claims_views
#from core.views import UnpaidDeliveriesTableView, UnplacedOrderTableView, OrderedUnacknowledgedOrdersTableView, UnpaidCommissionsTableView   
import core.views as core_views
from django.views.generic.edit import FormView
from orders.forms import OrderForm
from datetime import date
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#this_month_args = {'year':str(date.today().year), 'month':str(date.today().month)}

urlpatterns = patterns('',
    
    #home page template
    url(
      regex=r'^$',
      view=general_views.HomePageRedirectView.as_view(permanent=False),
      name="home",
    ),
    # url(r'^$', TemplateView.as_view(template_name='base.html')),  
    # url(r'^$', FormView.as_view(form_class=OrderForm, template_name = 'orders/form.html')),    
    
    url(
      regex= r'^orders/$',
      view=general_views.OrderMonthArchiveTableView.as_view(month_format='%m', year=str(date.today().year), month=str(date.today().month)),
      name="order_list",
    ),
    url(
      regex = r'^active-orders/$',
      view = general_views.ActiveOrdersTableView.as_view(),
      name = "active_orders",
    ),
    url(
      regex= r'^my-orders/$', 
      view=general_views.MyOrderListView.as_view(),
      name="my_order_list",
    ),
    url(
      regex = r'^orders/(?P<pk>\d+)/$', 
      view=order_crud_views.OrderDetailView.as_view(),
      name="order_detail",
    ),
    url(
      regex = r'^orders/(?P<pk>\d+)/edit/$', 
      view=login_required(order_crud_views.OrderUpdateView.as_view()),
      name="order_edit",
    ),
    url(
      regex = r'^orders/(?P<pk>\d+)/delete/$', 
      view=login_required(order_crud_views.OrderDeleteView.as_view()),
      name="order_delete",
    ),
    url(r'orders/add/$', login_required(order_crud_views.OrderCreateView.as_view()), name="order_add"),
    url(r'orders/(?P<pk>\d+)/delete/$', login_required(order_crud_views.OrderDeleteView.as_view()), name="order_delete"),

    # Archive Views
    # Month:
    url(
      # /2014/mar/
      regex = r'^orders/(?P<year>\d{4})/(?P<month>[a-zA-z]+)/$', 
      view=general_views.OrderMonthArchiveTableView.as_view(),
      name="archive_month",
    ),
    url(
      # /2014/03/
      regex = r'^orders/(?P<year>\d{4})/(?P<month>\d+)/$', 
      view=general_views.OrderMonthArchiveTableView.as_view(month_format='%m'),
      name="archive_month_numeric",
    ),
    url(
      # /this-month
      regex = r'^orders/this-month/$', 
      view=general_views.OrderMonthArchiveTableView.as_view(year=str(date.today().year), month=str(date.today().month), month_format='%m'),
      name="archive_this_month",
    ),

    # Alerts pages
    url(
      regex= r'^alerts/$', 
      view=core_views.UnplacedOrderTableView.as_view(),
      name="alerts_main",
    ),
    url(
      regex= r'^alerts/unpaid-deliveries/$', 
      view=core_views.UnpaidDeliveriesTableView.as_view(),
      name="alerts_unpaid_deliveries",
    ),
    url(
      regex= r'^alerts/unacknowledged-orders/$', 
      view=core_views.OrderedUnacknowledgedOrdersTableView.as_view(),
      name="alerts_unacknowledged_orders",
    ),
    url(
      regex= r'^alerts/unpaid-commissions/$', 
      view=core_views.UnpaidCommissionsTableView.as_view(),
      name="alerts_unpaid_commissions",
    ),
    url(
      regex= r'^alerts/protection-plan/$', 
      view=core_views.CryptonProtectionAlertTableView.as_view(),
      name="alerts_protection_plan",
    ),
     url(
      regex= r'^alerts/order-financing/$', 
      view=core_views.OrderFinancingAlertTableView.as_view(),
      name="alerts_order_financing",
    ),

    # Customer links
    url(
      regex = r'customers/$', 
      view = CustomerTableView.as_view(), 
      name="customer_list",
    ),
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

    # Sales Standings Report
    url(
      # /sales-standings/
      regex = r'^sales-standings/$', 
      view=general_views.SalesStandingsMonthTableView.as_view(),
      name="sales_standings_cur",
    ),
    url(
      regex = r'^sales-standings/commissions-scale/$',
      view=TemplateView.as_view(template_name="orders/commissions_scale.html"),
      name = "commissions_scale",
    ),
    url(
    	regex = r'^bonus-report/$',
    	view = BonusMonthlyReportView.as_view(),
      name = "bonus_report"
    ),

    # authentication-related URLs
#    url(
#      r'^accounts/login/$', 
#      'django.contrib.auth.views.login', 
#      {'template_name': 'login.html'},
#      name = 'login_url',
#    ),
    (r'^accounts/', include('django.contrib.auth.urls')),

    # search
    url(
      regex = r'^search/$',
      view = 'core.views.search',
      name = "search",
    ),

    # deliveries
    url(
      regex = r'^deliveries/$',
      view = deliveries_views.DeliveriesTableView.as_view() ,
      name = "delivery_list",
    ),
    url(
      regex = r'^deliveries/(?P<pk>\d+)/$', 
      view=deliveries_views.DeliveryDetailView.as_view(),
      name="delivery_detail",
    ),
    url(
      regex = r'^deliveries/(?P<pk>\d+)/edit/$', 
      view=deliveries_views.DeliveryUpdateView.as_view(),
      name="delivery_edit",
    ),
    url(
      regex = r'^deliveries(?P<pk>\d+)/delete/$', 
      view=deliveries_views.DeliveryDeleteView.as_view(),
      name="delivery_delete",
    ),
                       
    #claims
    url(
        regex = r'^claims/$',
        view = claims_views.ClaimsTableView.as_view() ,
        name = "claim_list",
    ),
    url(
      regex = r'^claims/(?P<pk>\d+)/$', 
      view=claims_views.ClaimDetailView.as_view(),
      name="claim_detail",
    ),
    url(
      regex = r'^claims/(?P<pk>\d+)/edit/$', 
      view=claims_views.ClaimUpdateView.as_view(),
      name="claim_edit",
    ),
    url(
      regex = r'^claims(?P<pk>\d+)/delete/$', 
      view=claims_views.ClaimDeleteView.as_view(),
      name="claim_delete",
    ),
    url(
        regex = r'claims/add/$', 
        view = claims_views.ClaimCreateView.as_view(), 
        name="claim_add"
    ),
    url(
        regex = r'claims/print/$',
        view = claims_views.claim_print,
        name="claim_print"
    ),

    url(r'^ajax_select/', include('ajax_select.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # administration URLs 
    url(r'^admin/', include(admin.site.urls)),

)

if settings.DEBUG:
    # development serve static files
    urlpatterns += patterns('', 
      (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
