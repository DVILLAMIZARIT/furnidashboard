from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.dates import MonthArchiveView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from crispy_forms.helper import FormHelper
from orders.models import Order, OrderItem, OrderDelivery, OrderIssue
from orders.tables import OrderTable
from orders.forms import OrderForm, CustomerFormSet, CommissionFormSet, ItemFormSet, get_ordered_items_formset, DeliveryFormSet, get_deliveries_formset, get_commissions_formset, OrderDeliveryForm, OrderItemFormHelper, OrderAttachmentFormSet, get_order_issues_formset
import orders.forms as order_forms
from orders.filters import OrderFilter
from customers.models import Customer
import core.utils as utils
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin

crypton_orphan_info_error = "Crypton protection information has been entered but 'Protection plan purchased' option is not selected. Either check the protection plan checkbox or delete Crypton protection information by selecting the 'Delete' checkbox."
order_financing_orphan_info_error = "Order financing information has been entered but 'Order financing' option is not selected. Either check the order financing checkbox or delete Order financing information by selecting the 'Delete' checkbox."
err_saving_order_info_msg = "Error saving the order information. Please go through tabs to fix invalid information."

err_invalid_delivered_status_msg = "Cannot set order status to 'Delivered' because there are no deliveries recorded for this order."
err_invalid_order_dummy_status_msg = "Cannot set order status to 'Dummy' because there are special order items."
err_invalid_new_order_status_msg = "Newly created order status must be either 'New', 'Pending', or 'Dummy'!"
err_missing_customer_info_msg = "Please select existing customer or fill in new customer information!"
err_cant_close_order_msg = "Cannot close the order while there are unpaid commissions due!"
err_blank_order_status_msg = "Order status cannot be blank!"

error_message_tag = "alert alert-danger"

class OrderDetailView(PermissionRequiredMixin, DetailView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_detail.html"

  required_permissions = (
    'orders.view_orders',
  )

  def get_context_data(self, **kwargs):
    context = super(OrderDetailView, self).get_context_data(**kwargs)
    user_model = get_user_model()
    return context

#-----------------------------------------------------------------------

class OrderDeleteView(PermissionRequiredMixin, DeleteView):
  model = Order
  context_object_name = "order"
  success_url = reverse_lazy("order_list")

  required_permissions = (
    'orders.delete_order',
  )

#-----------------------------------------------------------------------

class OrderUpdateView(PermissionRequiredMixin, UpdateView):
  model = Order
  context_object_name = "order"
  template_name = "orders/order_update.html"
  form_class = OrderForm

  required_permissions = (
    'orders.change_order',
  )

  def get(self, request, *args, **kwargs):
    """ 
    Handle GET requests and instantiate blank version of the form
    and it's inline formsets
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    self.request = request
    
    if not request.user.has_perm('orders.update_status'):
      #disable order status for staff person without privilege
      form.fields['status'].widget.attrs['readonly'] = 'readonly'
    
    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers") 

    extra = 1 if self.object.commission_set.count() == 0 else 0  #if no commissions were saved for this order, add a blank form
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(instance=self.object, prefix="commissions")
    
    extra = 1 if self.object.orderdelivery_set.count() == 0 else 0
    DeliveriesFormSet = get_deliveries_formset(extra=extra, max_num=100, request=self.request)
    delivery_form = DeliveriesFormSet(instance=self.object, prefix="deliveries")

    # prevent empty form showing up if no items were recorded for the order
    # specify at least 1 extra of no items are set
    extra = 1 if self.object.orderitem_set.count() == 0 else 0
    SoldItemsFormSet = get_ordered_items_formset(extra=extra, max_num=100)
    items_form = SoldItemsFormSet(instance=self.object, prefix="ordered_items")

    # attachments
    attachment_form = OrderAttachmentFormSet(instance=self.object, prefix="attachments")

    # issues form
    extra = 1 if self.object.orderissue_set.count() == 0 else 0
    OrderIssuesFormSet = get_order_issues_formset(extra=extra, max_num=100)
    issues_form = OrderIssuesFormSet(instance=self.object, prefix='issues')

    # crypton protection plan form
    crypton_protection_form = order_forms.CryptonProtectionFormSet(instance=self.object, prefix="crypton")

    # special financing option form
    order_financing_form = order_forms.OrderFinancingFormSet(instance=self.object, prefix="financing")

    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
      'attachment_form':attachment_form,
      'issues_form':issues_form,
      'crypton_form': crypton_protection_form,
      'financing_form': order_financing_form,
    }
    context = self.get_context_data()
    context.update(extra_forms)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    self.request = request
    
    if not request.user.has_perm('orders.update_status'):
      #disable order status for staff person without privilege
      form.fields['status'].widget.attrs['readonly'] = 'readonly'

    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")

    #commissions_form = CommissionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="commissions")
    extra = 1 if self.object.commission_set.count() == 0 else 0  #if no commissions were saved for this order, add a blank form
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="commissions")

    items_form = ItemFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="ordered_items")
    DeliveriesFormSet = get_deliveries_formset(extra=0, max_num=100, request=self.request)
    delivery_form = DeliveriesFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="deliveries")

    attachment_form = OrderAttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="attachments")

    OrderIssuesFormSet = get_order_issues_formset()
    issues_form = OrderIssuesFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="issues")

    crypton_protection_form = order_forms.CryptonProtectionFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="crypton")
    order_financing_form = order_forms.OrderFinancingFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="financing")

    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'delivery_form':delivery_form,
      'attachment_form':attachment_form,
      'issues_form': issues_form,
      'crypton_form': crypton_protection_form,
      'financing_form': order_financing_form,
    }

    #check if forms are valid
    forms_valid = form.is_valid()
    if forms_valid and commissions_form.has_changed():
      forms_valid = commissions_form.is_valid()
    if forms_valid and items_form.has_changed():  
      forms_valid = items_form.is_valid()
    if forms_valid :
      for form in [f for f in delivery_form.forms if f.has_changed()]: # and  f not in delivery_form.deleted_forms]:  
        forms_valid = form.is_valid()
        if not forms_valid:
          break
    if forms_valid and attachment_form.has_changed():  
      forms_valid = attachment_form.is_valid()
    if forms_valid and crypton_protection_form.has_changed():
      forms_valid = crypton_protection_form.is_valid()
    if forms_valid and order_financing_form.has_changed():
      forms_valid = order_financing_form.is_valid()
      
    if forms_valid:
      return self.form_valid(**forms)
    else:
      messages.add_message(self.request, messages.ERROR, err_saving_order_info_msg, extra_tags=error_message_tag)
      return self.form_invalid(**forms)

  def form_valid(self, *args, **kwargs):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    form = kwargs['form']
    customer_form = kwargs['customer_form']
    items_form = kwargs['items_form']
    commissions_form = kwargs['commissions_form']
    delivery_form = kwargs['delivery_form']
    attachment_form = kwargs['attachment_form']
    issues_form = kwargs.get('issues_form')
    crypton_protection_form = kwargs['crypton_form']
    order_financing_form  = kwargs['financing_form']
    
    orig_status = self.object.status
    self.object = form.save(commit=False)

    # flags
    BR_passed = True
    new_customer=False

    # import pdb; pdb.set_trace()

    # validate order status
    if not form.data['status'] :
      messages.error(self.request, err_blank_order_status_msg, extra_tags="alert")
      BR_passed = False
    else:
      new_status = form.cleaned_data['status']
      if new_status == 'C' and any([comm_data['paid'] == False for comm_data in commissions_form.cleaned_data]): 
        messages.add_message(self.request, messages.ERROR, err_cant_close_order_msg, extra_tags=error_message_tag)
        BR_passed = False
      elif new_status == 'D' and not [f for f in delivery_form if not utils.delivery_form_empty(f.cleaned_data)]:
        messages.add_message(self.request, messages.ERROR, err_invalid_delivered_status_msg, extra_tags=error_message_tag)
        BR_passed = False
      elif new_status == 'X' and any([i for i in items_form.cleaned_data if i['in_stock'] == False]):
        messages.add_message(self.request, messages.ERROR, err_invalid_order_dummy_status_msg, extra_tags=error_message_tag)
        BR_passed = False


    # validate customer
    if BR_passed:
      if self.object.customer is None:
        if customer_form.is_valid():
          # check that first and last name are filled
          try:
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, err_missing_customer_info_msg, extra_tags=error_message_tag)
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, err_missing_customer_info_msg, extra_tags=error_message_tag)
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer information!", extra_tags=error_message_tag)
          BR_passed = False

    # validate issues
    if BR_passed and not issues_form.is_valid():
      messages.error(self.request, "Error saving 'order issues' information!", extra_tags=error_message_tag)
      BR_passed = False

    # validate crypton protection plan
    if BR_passed and not self.object.protection_plan:
      if not _is_valid_protection_plan(crypton_protection_form):      
        messages.error(self.request, crypton_orphan_info_error, extra_tags=error_message_tag)
        BR_passed = False

    # validate order financing information
    if BR_passed and not self.object.financing_option:
      if not _is_valid_financing_plan(order_financing_form):
        messages.error(self.request, order_financing_orphan_info_error, extra_tags=error_message_tag)
        BR_passed = False  

    # Final check
    if BR_passed: 
      
      if not self.request.user.has_perm('orders.update_status'):
        if orig_status:
          self.object.status = orig_status #reset previous value
          messages.warning(self.request, "You don't have permission to change order status. Order status was reset to previous value.", extra_tags="alert")
        
      
      # save customer
      if new_customer:
        cust = customer_form[0].save()
        self.object.customer = cust

      #save order
      self.object.save()

      # save items
      if items_form.has_changed():
        items_form.instance = self.object
        items_form.save()

      # save commissions
      if commissions_form.has_changed():
        commissions_form.instance = self.object
        commissions_form.save()

      # save deliveries
      for del_form in delivery_form:
        if del_form.has_changed():
          if del_form.instance.pk or not utils.delivery_form_empty(del_form.cleaned_data):
            del_form.order = self.object
            del_form.save()
            if any(self.object.orderitem_set.filter(~Q(status__in=['S', 'R']))):
              messages.add_message(self.request, messages.ERROR, "Warning: a delivery has been scheduled for this order BUT item(s) are not in stock/not delivered. Please check the order status for any issues.", extra_tags="alert alert-warning")

      # save attachments
      if attachment_form.has_changed():
        attachment_form.instance = self.object
        attachment_form.save()
 
      # save issues
      if issues_form.has_changed():
        issues_form.instance = self.object
        issues_form.save()

      #save order protection plan form
      if crypton_protection_form.has_changed():
        crypton_protection_form.instance = self.object
        crypton_protection_form.save()

      #save order financing option form
      if order_financing_form.has_changed():
        order_financing_form.instance = self.object
        order_financing_form.save()

      return HttpResponseRedirect(self.get_success_url())

    else:
      return self.form_invalid(**kwargs)


  def form_invalid(self, *args, **kwargs):
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """
    context = self.get_context_data()
    #kwargs.update({'messages':messages.get_messages(self.request)})
    context.update(kwargs)

    return self.render_to_response(context)

  def get_context_data(self, **kwargs):
    context = super(OrderUpdateView, self).get_context_data(**kwargs)
    context['item_form_helper'] = OrderItemFormHelper
    return context

  def get_success_url(self):
    return self.get_object().get_absolute_url() #reverse('order_detail', kwargs={'pk': self.object.pk})



#------------------------------------------------------------------------

class OrderCreateView(PermissionRequiredMixin, CreateView):
  """
  Order Creation view. Presents blank forms for inputting new orders.
  """

  model = Order
  template_name = "orders/order_update.html"
  form_class = OrderForm

  required_permissions = (
    'orders.add_order',
  )

  def get(self, request, *args, **kwargs):
    """ 
    Handle GET requests and instantiate blank version of the form
    and it's inline formsets
    """
    self.object = None 
    form_class = self.get_form_class()
    form = self.get_form(form_class)

    # initialize form defaults
    form.fields['status'].widget.attrs['readonly'] = True

    customer_form = CustomerFormSet(queryset=Customer.objects.none(), prefix="customers")
    items_form = ItemFormSet(prefix="ordered_items")

    extra = 1 
    SpecialCommissionFormSet = get_commissions_formset(extra=extra, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(prefix="commissions")

    crypton_protection_form = order_forms.CryptonProtectionFormSet(prefix="crypton")

    order_financing_form = order_forms.OrderFinancingFormSet(prefix="financing")

    extra_forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'crypton_form': crypton_protection_form,
      'financing_form': order_financing_form,
    }
    context = self.get_context_data()
    context.update(extra_forms)
    return self.render_to_response(context)

  def post(self, request, *args, **kwargs):
    """
    Handles POST requests, instantiates a form instance and its inline formsets with the passed POST variables
    and then checks them for validity
    """

    self.object = None
    form_class = self.get_form_class()
    form = self.get_form(form_class)

    # initialize form defaults
    form.fields['status'].widget.attrs['readonly'] = True

    customer_form = CustomerFormSet(self.request.POST, self.request.FILES, prefix="customers")
    items_form = ItemFormSet(self.request.POST, self.request.FILES, prefix="ordered_items")

    SpecialCommissionFormSet = get_commissions_formset(extra=1, max_num=3, request=self.request)
    commissions_form = SpecialCommissionFormSet(self.request.POST, self.request.FILES, prefix="commissions")

    crypton_protection_form = order_forms.CryptonProtectionFormSet(self.request.POST, self.request.FILES, prefix="crypton")
    order_financing_form = order_forms.OrderFinancingFormSet(self.request.POST, self.request.FILES, prefix="financing")

    forms = {
      'form':form,
      'customer_form':customer_form,
      'items_form':items_form,
      'commissions_form':commissions_form,
      'crypton_form': crypton_protection_form,
      'financing_form': order_financing_form,
    }

    if form.is_valid() and items_form.is_valid() and commissions_form.is_valid() and crypton_protection_form.is_valid() and order_financing_form.is_valid(): 
      return self.form_valid(**forms)
    else:
      messages.add_message(self.request, messages.ERROR, err_saving_order_info_msg, extra_tags="alert alert-danger")
      return self.form_invalid(**forms)

  def form_invalid(self, *args, **kwargs): 
    """
    Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
    """    
    context = self.get_context_data()
    context.update(kwargs)
    return self.render_to_response(context)

  def form_valid(self, *args, **kwargs):
    """
    Called if all forms are valid. Creates an Order instance along with associated Customer and Commission instances
    and then redirects to a success page
    """
    form = kwargs['form']
    customer_form = kwargs['customer_form']
    items_form = kwargs['items_form']
    commissions_form = kwargs['commissions_form']
    crypton_protection_form = kwargs['crypton_form']
    order_financing_form  = kwargs['financing_form']

    self.object = form.save(commit=False)

    # flags
    BR_passed = True
    new_customer=False

    if not form.data['status'] or form.data['status'] not in ('Q', 'N', 'X'):
      messages.error(self.request, err_invalid_new_order_status_msg, extra_tags=error_message_tag)
      BR_passed = False

    # validate customer
    if BR_passed:

      if self.object.customer is None:
        if customer_form.has_changed() and customer_form.is_valid():
          try:
            # check that first and last name are filled
            if not customer_form[0].cleaned_data['first_name'] or not customer_form[0].cleaned_data['last_name']:
              messages.error(self.request, err_missing_customer_info_msg, extra_tags=error_message_tag)
              BR_passed = False
            else:
              new_customer = True
          except KeyError: 
            messages.error(self.request, err_missing_customer_info_msg, extra_tags=error_message_tag)
            BR_passed = False
        else:
          messages.error(self.request, "Error saving customer form information!", extra_tags=error_message_tag)
          BR_passed = False

    # validate crypton protection plan
    if BR_passed and not self.object.protection_plan:
      if not _is_valid_protection_plan(crypton_protection_form):      
        messages.error(self.request, crypton_orphan_info_error, extra_tags=error_message_tag)
        BR_passed = False

    # validate order financing information
    if BR_passed and not self.object.financing_option:
      if not _is_valid_financing_plan(order_financing_form):
        messages.error(self.request, order_financing_orphan_info_error, extra_tags=error_message_tag)
        BR_passed = False  

    if BR_passed: 
      
      # save customer
      if new_customer:
        cust = customer_form[0].save()
        self.object.customer = cust

      #save order
      self.object.save()

      # save items
      items_form.instance = self.object
      items_form.save()

      # save commissions
      commissions_form.instance = self.object
      commissions_form.save()

      #save order protection plan form
      if crypton_protection_form.has_changed():
        crypton_protection_form.instance = self.object
        crypton_protection_form.save()

      #save order financing option form
      if order_financing_form.has_changed():
        order_financing_form.instance = self.object
        order_financing_form.save()

      return HttpResponseRedirect(self.get_success_url())
    else:
      return self.form_invalid(**kwargs)

  def get_context_data(self, **kwargs):
    context = super(OrderCreateView, self).get_context_data(**kwargs)
    context['item_form_helper'] = OrderItemFormHelper
    return context

  def get_success_url(self):
    return reverse('order_detail', kwargs={'pk': self.object.pk})

#-----------------------------------------------------------------------

class OrderDeleteView(PermissionRequiredMixin, DeleteView):
  model = Order
  success_url = reverse_lazy("order_list")

  required_permissions = (
    'orders.delete_order',
  )


############################ UTILITY FUNCTIONS ######################################

def _is_valid_protection_plan(protection_plan_form):
  """
  function that checks if orphaned protection plan info exists while order's protection status flag is not set
  """
  for cleaned_data in protection_plan_form.cleaned_data:
    if cleaned_data:
      if 'DELETE' in cleaned_data and cleaned_data['DELETE']:
        continue #form row has been marked for deletion, skip it
      else:
        #check if specified fields are populated in the form
        if _any_form_fields_entered(cleaned_data, ('approval_no', 'details')):
          return False
  return True

def _is_valid_financing_plan(financing_plan_form):
  """
  function that checks if orphaned financing plan info exists while order's financing plan status flag is not set.
  this data has similar structure to 'protection plan' that is why it refers to protection plan validation function
  """
  return _is_valid_protection_plan(financing_plan_form)  

def _any_form_fields_entered(cleaned_data, field_list):
  """
  function that checks whether a form has any specified fields filled out (not blank)
  """
  res = False
  for field in field_list:
    if field in cleaned_data:
      if len(cleaned_data[field]):
        res = True
        break

  return res

