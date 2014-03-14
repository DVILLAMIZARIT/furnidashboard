from django.contrib import admin
from .models import Lead

class LeadAdmin(admin.ModelAdmin):
  #fields = ['first_name', 'last_name', 'email', 'owner']
  fieldsets = [
    ('Lead information', {'fields': ['first_name', 'last_name', 'email']}),
    (None,               {'fields': ['owner']}),
  ]

  list_display = ('created', 'last_name', 'first_name')

  #filtering
  list_filter = ['created', 'modified']
  search_fields = ['first_name', 'last_name', 'email']

admin.site.register(Lead, LeadAdmin)
