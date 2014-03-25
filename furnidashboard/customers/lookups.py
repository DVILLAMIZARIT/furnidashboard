from customers.models import Customer
from django.db.models import Q

class CustomerLookup(object):

  def get_query(self,q,request):
      """ return a query set.  you also have access to request.user if needed """
      return Customer.objects.filter(Q(first_name__istartswith=q) | Q(last_name__istartswith=q) | Q(email__icontains=q))

  def format_result(self, customer):
      """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
      return u"%s %s (%s)" % (customer.first_name, customer.last_name, customer.email)

  def format_item(self, customer):
      """ the display of a currently selected object in the area below the search box. html is OK """
      return unicode(customer)

  def get_objects(self,ids):
      """ given a list of ids, return the objects ordered as you would like them on the admin page.
          this is for displaying the currently selected items (in the case of a ManyToMany field)
      """
      return Customer.objects.filter(pk__in=ids).order_by('first_name', 'last_name')
