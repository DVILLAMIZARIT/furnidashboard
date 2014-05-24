from django.contrib.humanize.templatetags.humanize import intcomma

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
  import pdb; pdb.set_trace()
  return form_data['delivery_type'] != None
  
