from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy, reverse
import django_tables2 as tables
from django_tables2 import RequestConfig, SingleTableView
from django.contrib import messages
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.utils import timezone
from claims.models import Claim, ClaimStatus, ClaimPhoto
from claims.tables import ClaimsTable
import claims.forms as claim_forms
from datetime import datetime
from django.http import HttpResponse
from pdf import pdf

class ClaimsTableView(LoginRequiredMixin, SingleTableView):
  model = Claim
  table_class = ClaimsTable
  template_name = "claims/claims_table.html"
  
  
class ClaimDetailView(LoginRequiredMixin, DetailView):
  model = Claim
  context_object_name = "claim"
  template_name = "claims/claim_detail.html"
  
class ClaimCreateView(PermissionRequiredMixin, CreateView):
    """
    Claim Creation view. Presents blank forms for creation of new claims.
    """
    
    model = Claim
    template_name = "claims/claim_update.html"
    context_object_name = "claim"
    form_class = claim_forms.ClaimForm
    
    required_permissions = (
      'claims.edit_claims',
    )
  
    def get(self, request, *args, **kwargs):
        """ 
        Handle GET requests and instantiate blank version of the form
        and it's inline formsets
        """

        cur_date = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.fields['claim_date'].initial = cur_date

        status_initial = [{
            'date': cur_date,
            'status': 'NEW',
            'status_desc': 'New claim entered'
        }]
        ClaimStatusFormSet = claim_forms.get_claim_status_formset(extra=1)
        claim_status_formset = ClaimStatusFormSet(prefix="status", initial=status_initial)
        
        ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra = 1)
        claim_photos_formset = ClaimPhotoFormSet(prefix="photos")
        
        extra_forms = {
          'form':form,
          'status_formset': claim_status_formset,
          'photos_formset': claim_photos_formset,
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
        
        ClaimStatusFormSet = claim_forms.get_claim_status_formset(extra=1)
        claim_status_formset = ClaimStatusFormSet(self.request.POST, self.request.FILES, prefix="status")
        
        ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra = 1)
        claim_photos_formset = ClaimPhotoFormSet(self.request.POST, self.request.FILES, prefix="photos")
        
        extra_forms = {
          'form':form,
          'status_formset': claim_status_formset,
          'photos_formset': claim_photos_formset,
        }
        
        if form.is_valid() and claim_status_formset.is_valid() and claim_photos_formset.is_valid(): 
            return self.form_valid(**extra_forms)
        else:
            messages.add_message(self.request, messages.ERROR, "Error saving Claim information", extra_tags="alert alert-danger")
            return self.form_invalid(**extra_forms)
        
    def form_valid(self, *args, **kwargs):
        """
        Called if all forms are valid. Creates a Claim instance along with associated info
        and then redirects to a success page
        """
        form = kwargs['form']
        status_formset = kwargs['status_formset']   
        photos_formset = kwargs['photos_formset']     

        self.object = form.save(commit=False)

        #save order
        self.object.save()

        # save status
        if status_formset.has_changed():
            status_formset.instance = self.object
            status_formset.save()
            
        # save photos
        if photos_formset.has_changed():
            photos_formset.instance = self.object
            photos_formset.save()

        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('claim_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, *args, **kwargs): 
        """
        Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
        """    
        context = self.get_context_data()
        context.update(kwargs)
        return self.render_to_response(context)   
  
  
class ClaimUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Claim Update view. 
    """
    
    model = Claim
    context_object_name = "claim"
    template_name = "claims/claim_update.html"
    form_class = claim_forms.ClaimForm
    
    required_permissions = (
      'claims.edit_claims',
    )
    
    def get(self, request, *args, **kwargs):
        """ 
        Handle GET requests and instantiate blank version of the form
        and it's inline formsets
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        extra = 1 if self.object.claimstatus_set.count() == 0 else 0  #if no statuses were entered for the claim, add a blank form
        ClaimStatusFormSet = claim_forms.get_claim_status_formset(extra=extra)
        claim_status_formset = ClaimStatusFormSet(instance=self.object, prefix="status")
        
        extra = 1 #if self.object.claimphoto_set.count() == 0 else 0  #if no statuses were entered for the claim, add a blank form
        ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra = extra)
        claim_photos_formset = ClaimPhotoFormSet(instance=self.object, prefix="photos")
        
        extra_forms = {
          'form':form,
          'status_formset': claim_status_formset,
          'photos_formset': claim_photos_formset,
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
        
        ClaimStatusFormSet = claim_forms.get_claim_status_formset(extra=1)
        claim_status_formset = ClaimStatusFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="status")
        
        ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra = 1)
        claim_photos_formset = ClaimPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="photos")
        
        extra_forms = {
          'form':form,
          'status_formset': claim_status_formset,
          'photos_formset': claim_photos_formset,
        }
        
        if form.is_valid() and claim_status_formset.is_valid() and claim_photos_formset.is_valid(): 
            return self.form_valid(**extra_forms)
        else:
            messages.add_message(self.request, messages.ERROR, "Error saving Claim information", extra_tags="alert alert-danger")
            return self.form_invalid(**extra_forms)
        
    def form_valid(self, *args, **kwargs):
        """
        Called if all forms are valid. Creates a Claim instance along with associated info
        and then redirects to a success page
        """
        form = kwargs['form']
        status_formset = kwargs['status_formset']        
        photos_formset = kwargs['photos_formset']

        self.object = form.save(commit=False)

        #save order
        self.object.save()

        # save status
        if status_formset.has_changed():
            status_formset.instance = self.object
            status_formset.save()
            
         # save photos
        if photos_formset.has_changed():
            photos_formset.instance = self.object
            photos_formset.save()

        return HttpResponseRedirect(self.get_success_url())

        #return self.form_invalid(**kwargs)
    
    def get_success_url(self):
        return reverse('claim_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, *args, **kwargs): 
        """
        Called if any of the forms on order page is invalid. Returns a response with an invalid form in the context
        """    
        context = self.get_context_data()
        context.update(kwargs)
        return self.render_to_response(context)    


  
class ClaimDeleteView(LoginRequiredMixin, DeleteView):
  model = Claim
  success_url = reverse_lazy("claim_list")


def claim_print(request, template_name='pdf/Natuzzi_service_request_form.pdf', **kwargs):
    context = {
        'FirstName': 'Emil',
        'LastName': 'Akhmirov',
        'ClaimDate': '11/14/2015',
        'AddressLine1': '5270 Auburn Blvd',
        'AddressLine2': 'Sacramento, CA 95841',
        'ChkRevive': '1',
        'Model1':'Re-Vive chair',
        'Version1': 'Leather',
        'Style1': 'style 1',
        'Description1': 'Damaged chair',
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = \
        'attachment; filename=Natuzzi_service_request_form.pdf'

    template = pdf.get_template(template_name)
    response.write(template.render(context))

    return response