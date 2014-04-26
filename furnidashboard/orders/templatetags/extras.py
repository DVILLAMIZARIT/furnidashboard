from django import template
from core.utils import dollars

register = template.Library()

register.filter('dollars', dollars)
