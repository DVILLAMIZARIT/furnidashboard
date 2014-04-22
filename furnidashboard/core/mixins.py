from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

class LoginRequiredMixin(object):
  @method_decorator(login_required)
  def dispatch(self, request, *args, **kwargs):
    return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class PermissionRequiredMixin(object):
  """ A view mixin which verifie that the logged in user has the specified
  permissions.
  Settings:
  `required_permissions` - list/tuple of required permissions

  Example Usage:
    
    class SomeView(PermissionRequiredMixin, ListView):
      ...
      required_permissions = (
        'app1.permission_a',
        'app2.permission_b',
      )
      ...
  """
  required_permissions = ()

  @method_decorator(login_required)
  def dispatch(self, request, *args, **kwargs):
    if not request.user.has_perms(self.required_permissions):
      messages.error(
          request,
          'You do not have the permission required to perform the requested operation'
          )
      return redirect(reverse('login_url'))

    return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)

class DisabledFieldsMixin(object):
  def __init__(self, *args, **kwargs):
    super(DisabledFieldsMixin,self).__init__(*args, **kwargs)
    for field in (field for name, field in self.fields.iteritems()):
      field.widget.attrs['disabled'] = 'disabled'
      field.required = False

  def clean(self):
    cleaned_data = super(DisabledFieldsMixin, self).clean()
    for field in (field for name, field in self.fields.iteritems()):
      cleaned_data[field] = getattr(self.instance, field)

    return cleaned_data

