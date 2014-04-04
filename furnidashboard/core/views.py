import re
from django.db.models import Q
from orders.models import Order
from django.shortcuts import render

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S)').findall, normspaces=re.compile(r'\s{2,}').sub):
  """ Splits the query string in individual keywords, getting rid of unnecessary spaces and grouping quoted words together.
      Example:
      >>> normalize_query(' soem random words "with quotes " and    spaces')
      >>> ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
  """

  return [normspaces(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
  """ Returns a query that is a combination of Q objects. That combination aims to search keywords within a model by testing the given search fields
  """

  query = None # Query to search for every search term

  terms = normalize_query(query_string)
  for term in terms:
    or_query = None # Query to search for a given term in each field
    for field_name in search_fields:
      q = Q(**{"%s__icontains" % field_name: term})
      if or_query is None:
        or_query = q
      else:
        or_query = or_query | q
    if query is None:
      query = or_query
    else:
      query = query & or_query
  return query

def search(request):
  query_string = ''
  found_entries = None
  if request.GET:
    query_string = request.GET.get('q', '').strip()

    if query_string:

      entry_query = get_query(query_string, ['number',]) #, 'comments',])

      found_entries = Order.objects.filter(entry_query).order_by('-created')

      return render(request, 'search/search_results.html', 
        {'query_string': query_string, 
         'found_entries': found_entries},
        )
