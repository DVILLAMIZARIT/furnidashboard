from django.conf import settings
from django.core.files import File
#from django.core.files.temp import TemporaryFile
from tempfile import TemporaryFile
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy, reverse
import django_tables2 as tables
from django_tables2 import RequestConfig, SingleTableView
from django.contrib import messages
from core.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.utils import timezone
from claims.models import Claim, ClaimStatus, ClaimPhoto, VendorClaimRequest
from claims.tables import ClaimsTable
import claims.utils as claim_utils
import claims.forms as claim_forms
from datetime import datetime, timedelta
from django.http import HttpResponse
from pdf import pdf
import core.utils as core_utils
import json


class ClaimsTableView(LoginRequiredMixin, SingleTableView):
	model = Claim
	table_class = ClaimsTable
	template_name = "claims/claims_table.html"

	def get_queryset(self):
		qs = Claim.objects.all()
		# try:
		#     status = self.request.GET['status_filter']
		#     qs = claim_utils.filter_claims_by_latest_status(qs, status)
		# except KeyError, e:
		#     pass
		#
		# try:
		#     date_range = self.request.GET['date_range']
		#     self.from_date, self.to_date = core_utils.get_date_range_from_string(date_range)
		#     lookup_kwargs = {
		#         '%s__gte' % 'claim_date': self.from_date -  timedelta(minutes=1),
		#         '%s__lt' % 'claim_date': self.to_date,
		#     }
		#     qs = qs.filter(**lookup_kwargs)
		# except KeyError, e:
		#     pass

		return qs


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

		ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra=1)
		claim_photos_formset = ClaimPhotoFormSet(prefix="photos")

		extra_forms = {
			'form': form,
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

		ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra=1)
		claim_photos_formset = ClaimPhotoFormSet(self.request.POST, self.request.FILES, prefix="photos")

		extra_forms = {
			'form': form,
			'status_formset': claim_status_formset,
			'photos_formset': claim_photos_formset,
		}

		if form.is_valid() and claim_status_formset.is_valid() and claim_photos_formset.is_valid():
			return self.form_valid(**extra_forms)
		else:
			messages.add_message(self.request, messages.ERROR, "Error saving Claim information",
								 extra_tags="alert alert-danger")
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

		# save order
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

		extra = 1 if self.object.claimstatus_set.count() == 0 else 0  # if no statuses were entered for the claim, add a blank form
		ClaimStatusFormSet = claim_forms.get_claim_status_formset(extra=extra)
		claim_status_formset = ClaimStatusFormSet(instance=self.object, prefix="status")

		extra = 1  # if self.object.claimphoto_set.count() == 0 else 0  #if no statuses were entered for the claim, add a blank form
		ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra=extra)
		claim_photos_formset = ClaimPhotoFormSet(instance=self.object, prefix="photos")

		extra_forms = {
			'form': form,
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
		claim_status_formset = ClaimStatusFormSet(self.request.POST, self.request.FILES, instance=self.object,
												  prefix="status")

		ClaimPhotoFormSet = claim_forms.get_claim_photos_formset(extra=1)
		claim_photos_formset = ClaimPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object,
												 prefix="photos")

		extra_forms = {
			'form': form,
			'status_formset': claim_status_formset,
			'photos_formset': claim_photos_formset,
		}

		if form.is_valid() and claim_status_formset.is_valid() and claim_photos_formset.is_valid():
			return self.form_valid(**extra_forms)
		else:
			messages.add_message(self.request, messages.ERROR, "Error saving Claim information",
								 extra_tags="alert alert-danger")
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

		# save order
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

		# return self.form_invalid(**kwargs)

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
		'Model1': 'Re-Vive chair',
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


class VendorClaimRequestCreateView(PermissionRequiredMixin, CreateView):
	"""
	Claim Creation view. Presents blank forms for creation of new claims.
	"""

	model = VendorClaimRequest
	context_object_name = "claim_vendor_request"

	required_permissions = (
		'claims.edit_claims',
	)

	def get_template_names(self):
		return [u'claims/vendor_claim/natuzzi_request_form.html']

	def get_pdf_template_name(self):
		return u'pdf/Natuzzi_service_request_form.pdf'

	def get_form_class(self):
		if self.claim.item_origin in ('NTZ', 'EDITIONS', 'REVIVE'):
			return claim_forms.NatuzziClaimVendorRequestForm

	def get(self, request, *args, **kwargs):
		"""
		Handle GET requests and instantiate blank version of the form
		and it's inline formsets
		"""
		import logging
		logger = logging.getLogger("furnicloud")
		logger.debug(kwargs)

		self.object = None

		claim_pk = kwargs.get('claim_pk')
		self.claim = get_object_or_404(Claim, pk=claim_pk)

		form = self.get_form(self.get_form_class())

		if self.claim.delivery_date :
			delivery_dt =self.claim.delivery_date.strftime('%m/%d/%Y')
		else :
			delivery_dt = ''

		form.initial = {
			'claim': self.claim,
			'first_name': self.claim.customer.first_name or '',
			'last_name': self.claim.customer.last_name or '',
			'claim_date': self.claim.claim_date.strftime('%m/%d/%Y') or '',
			'address_line_1': self.claim.customer.shipping_address or '',
			'phone_num_home': self.claim.customer.phone or '',
			'email': self.claim.customer.email or '',
			'chk_editions': self.claim.item_origin == 'EDITIONS',
			'chk_revive': self.claim.item_origin == 'REVIVE',
			'chk_softaly': self.claim.item_origin == 'SOFTALY',
			'chk_italia': self.claim.item_origin == 'NTZ',
			'delivery_date': delivery_dt, 
			'descr_1': self.claim.claim_desc,
		}

		extra_forms = {
			'form': form,
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
		claim_pk = kwargs.get('claim_pk')
		self.claim = get_object_or_404(Claim, pk=claim_pk)
		form = self.get_form(self.get_form_class())

		extra_forms = {
			'form': form,
		}

		if form.is_valid():
			return self.form_valid(**extra_forms)
		else:
			messages.add_message(self.request, messages.ERROR, "Error saving  Vendor Request Claim information",
								 extra_tags="alert alert-danger")
			return self.form_invalid(**extra_forms)

	def form_valid(self, *args, **kwargs):
		"""
		Called if all forms are valid. Creates a Claim instance along with associated info
		and then redirects to a success page
		"""
		form = kwargs['form']

		self.object = form.save(commit=False)

		import logging
		logger = logging.getLogger("furnicloud")
		logger.debug(form.get_data_fields_dict())

		# save data fields to model instance
		data_fields = form.cleaned_data
		del data_fields['claim']
		del data_fields['file']
		self.object.data_fields = json.dumps(data_fields)

		# generate PDF claim request file and save to model instance field
		pdf_template = self.get_pdf_template_name()
		template = pdf.get_template(pdf_template)
		context = form.get_data_fields_dict()
		with TemporaryFile(mode="w+b") as f: #open('', 'wb') as f:
			pdf_contents = template.render(context) 
			f.write(pdf_contents)
			#f.write(json.dumps(context))
			f.seek(0) # go to beginning of file
			#reopen = open('/tmp/claim.pdf', 'rb')
			claim_file = File(f)
			date_str = datetime.now().strftime("%Y_%m_%d")
			self.object.file.save("claim_request" + date_str + ".pdf", claim_file, save=True)

		# save order
		self.object.save()

		#response = HttpResponse(content_type='application/pdf')
		#response['Content-Disposition'] = \
		#	'attachment; filename=Natuzzi_service_request_form.pdf'

		#response.write(pdf_contents)
		#return response

		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('claim_detail', kwargs={'pk': self.object.claim.pk})


class VendorClaimRequestDeleteView(LoginRequiredMixin, DeleteView):
	model = VendorClaimRequest

	def get_success_url(self):
		return reverse("claim_detail", kwargs={'pk':self.object.claim_id})
