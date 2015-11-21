from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q
from django.conf import settings
from orders.models import Order, OrderDelivery
from datetime import datetime, timedelta
import calendar


def dollars(dollars):
	dollars = round(float(dollars), 2)
	return "$ {0}{1}".format(intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])


def is_user_delivery_group(request):
	"""
  Determine if currently logged in user belongs to delivery_persons group
  """
	return request.user.groups.filter(name="delivery_persons").exists()


def delivery_form_empty(form_data):
	'''
  Check if delivery form is empty to determine if we need to save the instance
  '''
	return form_data['delivery_type'] == None


def get_unpaid_deliveries_queryset():
	return OrderDelivery.objects.filter(Q(paid=False) & ~Q(delivery_type='SELF'))


def get_unpaid_commissions_data():
	'''
  returns 'commissions due' list for table display 
  '''
	res = []

	order_list = Order.objects.commissions_unpaid()
	for o in order_list:
		split_num = o.commission_set.count()
		comm_queryset = o.commission_set.select_related().all()
		for com in comm_queryset:
			sales_amount = o.subtotal_after_discount / split_num
			comm_amount = sales_amount * settings.COMMISSION_PERCENT
			commissions_due = 0.0

			if not com.paid:
				# if order is Delivered, or Closed, commission is due
				commissions_due = comm_amount

			res.append({
				'associate': com.associate,
				'order_date': o.order_date.strftime("%m/%d/%y"),
				'order': o,
				'order_total': '{0:.2f}'.format(sales_amount),
				'commissions_due': '{0:.2f}'.format(commissions_due)
			})

	return res


def get_month_date_range(month, year):
	# 1st day of month
	from_date = datetime(year, month, 1)

	# get last day of month
	wkday, num_days = calendar.monthrange(year, month)
	to_date = from_date + timedelta(days=num_days)

	return (from_date, to_date)


def get_current_month_date_range():
	to_date = datetime.now()  # cur date

	return get_month_date_range(to_date.month, to_date.year)


def get_date_range_from_string(range_str, request):
	to_date = datetime.now()
	if range_str == 'week':
		from_date = to_date - timedelta(days=to_date.weekday())
		from_date = from_date.replace(hour=0, minute=0, second=0)
	if range_str == 'last-week':
		to_date = to_date - timedelta(days=to_date.weekday())
		to_date = to_date.replace(hour=0, minute=0, second=0)
		from_date = to_date - timedelta(days=7)
	elif range_str == 'month':
		from_date = datetime(to_date.year, to_date.month, 1)
	elif range_str == 'last-month':
		to_date = datetime(to_date.year, to_date.month, 1)
		from_date = to_date - timedelta(days=1)
		from_date = datetime(from_date.year, from_date.month, 1)
	elif range_str == 'year':
		from_date = datetime(to_date.year, 1, 1)
	elif range_str == 'custom':
		try:
			from_date = datetime.strptime(request.GET['range_from'], "%Y-%m-%d")
			to_date = datetime.strptime(request.GET['range_to'], "%Y-%m-%d")
			to_date = to_date.replace(hour=23, minute=59, second=59)
		except (KeyError, ValueError) as e:
			# raise ValueError("Incorrect date format, should be YYYY-MM-DD")
			messages.add_message(request, messages.ERROR, "Incorrect date format, should be YYYY-MM-DD",
			                     extra_tags="alert alert-danger")
			from_date = to_date - timedelta(days=to_date.weekday())
			from_date = from_date.replace(hour=0, minute=0, second=0)
	else:  # default
		from_date = to_date - timedelta(days=to_date.weekday())
		from_date = from_date.replace(hour=0, minute=0, second=0)

	return from_date, to_date
