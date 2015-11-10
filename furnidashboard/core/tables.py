import django_tables2 as tables
from django.utils.safestring import mark_safe

class CustomTextLinkColumn(tables.LinkColumn):
  def __init__(self, viewname, urlconf=None, args=None, kwargs=None, current_app=None, attrs=None, custom_text=None, **extra):
    super(CustomTextLinkColumn, self).__init__(viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app, attrs=attrs, **extra)
    self.custom_text = custom_text

  def render(self, value, record, bound_column):
    return super(CustomTextLinkColumn, self).render(self.custom_text if self.custom_text else value, record, bound_column)

class TruncateTextColumn(tables.Column):

    def __init__(self, trunc_length=30, *args, **kwargs):
        self.trunc_length=trunc_length
        super(TruncateTextColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return mark_safe(value[:self.trunc_length] + '...' if len(value) > self.trunc_length else value)

