from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class LoginRequiredMixin(object):
  @method_decorator(login_required)
  def dispatch(self, request, *args, **kwargs):
    return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

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
