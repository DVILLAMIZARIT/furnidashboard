from django.views.generic import UpdateView 
from django.views.generic.edit import CreateView, DeleteView
from django.contrib import messages
from .models import OrderIssue

class OrderIssueCreateView(PermissionRequiredMixin, CreateView):
  model = OrderIssue
  order = None

  def dispatch(self, request, *args, **kwargs):
    if not self.order: 
      messages.add_message(self.request, messages.ERROR, "Invalid order number specified!", extra_tags="alert alert-danger")

      return redirect(reverse('home'))

    return super(OrderIssueCreateView, self).dispatch(request, *args, **kwargs)
