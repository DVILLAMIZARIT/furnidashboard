from datetime import timedelta, date, datetime
from django.views.generic import ListView, DetailView, UpdateView, RedirectView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView
from django.core.urlresolvers import reverse_lazy, reverse
from django_tables2 import RequestConfig
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from orders.models import Order
from orders.tables import OrderTable, SalesByAssociateTable, SalesTotalsTable, SalesByAssocSalesTable
from orders.filters import OrderFilter
import orders.forms as order_forms
import orders.utils as order_utils
import core.utils as utils
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
        # self.filter.helper = self.formhelper_class()
        self.filter.helper.form_id = self.filter_form_id
        # self.filter.helper.form_class = "blueForms, well"
        self.filter.helper.form_method = "get"
        # self.filter.helper.add_input(Submit('submit', 'Submit'))

    def get_table(self, **kwargs):
        try:
            page = self.kwargs['page']
        except KeyError:
            page = 1
        options = {'paginate': {'page': page, 'per_page': self.table_paginate_by}}
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


# -----------------------------------------------------------------------

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

        # calc YTD stats
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
        ytd_totals_table = _get_sales_totals(ytd_orders)
        RequestConfig(self.request).configure(ytd_totals_table)
        context['ytd_totals_table'] = ytd_totals_table

        # calc sales totals by associate
        sales_by_assoc_data, tmp = order_utils.get_sales_data_from_orders(unfiltered_orders)
        sales_by_assoc = SalesByAssociateTable(sales_by_assoc_data)
        RequestConfig(self.request).configure(sales_by_assoc)
        context['sales_by_associate'] = sales_by_assoc

        # links to other months data
        context['order_months_links'] = self._get_month_list_for_year()
        context['previous_year_links'] = self._get_month_list_for_year(datetime.now().year - 1)
        context['prev_year'] = datetime.now().year - 1

        context['months_2013'] = self._get_month_list_for_year(datetime.now().year - 2)

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
        return [(name, reverse('archive_month_numeric', kwargs={'year': year, 'month': m})) for m, name in
                sorted(months_data)]

    def get_month_dated_queryset(self):
        year = self.get_year()
        month = self.get_month()
        date_field = self.get_date_field()
        date = datetime.strptime("-".join((year, month)),
                                 "-".join((self.get_year_format(), self.get_month_format()))).date()
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_month(date))
        lookup_kwargs = {
            '%s__gte' % date_field: since,
            '%s__lt' % date_field: until,
        }
        qs = self.model._default_manager.all().filter(**lookup_kwargs)

        return qs


# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------

class MyOrderListView(PermissionRequiredMixin, FilteredTableMixin, ListView):
    model = Order
    context_object_name = "order_list"
    # template_name = "orders/order_filtered_table.html"
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


# -----------------------------------------------------------------------

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
        # qs = super(FilteredTableMixin, self).get_queryset(**kwargs)
        date_range = "month" #default
        try:
            date_range = self.request.GET['date_range']
        except KeyError, e:
            pass

        self.from_date, self.to_date = utils.get_date_range_from_string(date_range, self.request);

        qs = Order.objects.get_dated_qs(self.from_date, self.to_date)

        return qs

    def get_context_data(self, **kwargs):
        context = super(SalesStandingsMonthTableView, self).get_context_data(**kwargs)

        date_range = 'month'
        if self.request.GET.has_key("date_range"):
            context['date_range_filter'] = order_forms.DateRangeForm(self.request.GET)
        else:
            context['date_range_filter'] = order_forms.DateRangeForm(initial={'date_range': date_range})

        context['dates_caption'] = "{0} - {1}".format(self.from_date.strftime("%Y-%m-%d"),
                                                      self.to_date.strftime("%Y-%m-%d"))

        orders = context[self.context_object_name]
        sales_by_assoc_data, sales_by_assoc_expanded_data = order_utils.get_sales_data_from_orders(orders)

        # total sales table
        sales_by_assoc_table = SalesByAssociateTable(sales_by_assoc_data)
        RequestConfig(self.request, paginate=False).configure(sales_by_assoc_table)
        context['sales_by_associate'] = sales_by_assoc_table

        # prepare expanded sales tables per each associate
        sales_by_assoc_expanded_tables = {}
        count = 1
        for assoc, sales in sales_by_assoc_expanded_data.items():
            sales_by_assoc_expanded_tables[assoc] = SalesByAssocSalesTable(sales, prefix="tbl" + str(count))
            RequestConfig(self.request).configure(sales_by_assoc_expanded_tables[assoc])
            count += 1
        context['sales_by_assoc_expanded_tables'] = sales_by_assoc_expanded_tables

        # sales by stores table
        store_totals_table = _get_sales_totals(orders)
        RequestConfig(self.request, paginate=False).configure(store_totals_table)
        context['store_totals_table'] = store_totals_table

        # employee of the month
        last_month_begin, last_month_end = utils.get_date_range_from_string('last-month', self.request)
        last_month_orders = Order.objects.get_dated_qs(last_month_begin, last_month_end)
        last_month_sales, _ = order_utils.get_sales_data_from_orders(last_month_orders)
        last_month_sales = sorted(last_month_sales, key=lambda a: a['sales'], reverse=True)
        try:
            context['employee_of_the_month'] = last_month_sales[0]['associate']
            context['employee_of_the_month_period'] = last_month_begin.strftime("%b, %Y")
        except (KeyError, IndexError):
            context['employee_of_the_month_period'] = context['employee_of_the_month'] = ''

        # sales_by_assoc_data_ytd = order_utils._calc_sales_assoc_by_orders(self.queryset)
        # sales_by_assoc_ytd = SalesByAssociateTable(sales_by_assoc_data_ytd)
        # RequestConfig(self.request).configure(sales_by_assoc_ytd)
        # context['sales_by_associate_ytd'] = sales_by_assoc_ytd

        # context['sales_data_ytd_raw'] = json.dumps([{'key':data['associate'], 'value':data['sales']} for data in sales_by_assoc_data])

        return context


# -----------------------------------------------------------------------

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
            {'item': 'Subtotal After Discount', 'hq': utils.dollars(subtotal_hq), 'fnt': utils.dollars(subtotal_fnt),
             'total': utils.dollars(subtotal_hq + subtotal_fnt)},
            {'item': 'Grand Total', 'hq': utils.dollars(total_hq), 'fnt': utils.dollars(total_fnt),
             'total': utils.dollars(total_hq + total_fnt)},
        ]
    totals_table = SalesTotalsTable(totals_data)
    return totals_table
