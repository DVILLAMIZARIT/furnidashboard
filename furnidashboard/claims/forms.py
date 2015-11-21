from django.utils import formats

from claims.models import Claim, ClaimStatus, ClaimPhoto, VendorClaimRequest
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms.utils import ErrorList
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.widgets import Select, HiddenInput
from django.contrib.auth import get_user_model
from django.utils.functional import curry
from django.conf import settings
from ajax_select.fields import AutoCompleteSelectField
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput
from core.mixins import DisabledFieldsMixin
from django.db.models import Q
import core.utils as utils
import orders.utils as order_utils
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field, HTML
from crispy_forms.bootstrap import AppendedText, InlineField

DATEPICKER_OPTIONS = {"format":"YYYY-MM-DD", "pickTime": False}

class ClaimForm(forms.ModelForm):

    customer = AutoCompleteSelectField('customer', required=False)
    order_ref = AutoCompleteSelectField('order', required=False)

    def __init__(self, *args, **kwargs):
        super(ClaimForm, self).__init__(*args, **kwargs)

        self.fields['claim_date'].label = "Claim Date"
        self.fields['claim_date'].widget = DateTimePicker(options=DATEPICKER_OPTIONS)

        self.fields['delivery_date'].label = "Delivery Date"
        self.fields['delivery_date'].widget = DateTimePicker(options=DATEPICKER_OPTIONS)

        self.fields['order_invoice_num'].label = "Vendor Order/invoice #"
        self.fields['order_ref'].label = "FurniCloud Order"
    
    class Meta:
        model = Claim
        fields = "__all__"


class ClaimStatusForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClaimStatusForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = DateTimePicker(options=DATEPICKER_OPTIONS)
        self.fields['date'].label = "Status Date"
        
        self.fields['status'].label = "Status"
        
        self.fields['status_desc'].widget.attrs['size']=80
    
    class Meta:
        model = ClaimStatus
        fields = "__all__" 

class ClaimPhotoForm(forms.ModelForm):

    pass

    class Meta:
        model = ClaimPhoto
        fields = "__all__"


class NatuzziClaimVendorRequestForm(forms.ModelForm):

    NTZ_BRAND_CHOICES = (
        ('NTZ', 'Natuzzi Italia'),
        ('EDITIONS', 'Natuzzi Editions'),
        ('REVIVE', 'Natuzzi Re-Vive'),
        ('SOFTALY', 'Softaly'),
    )

    first_name = forms.CharField(label="Customer First Name", required=False)
    last_name = forms.CharField(label="Customer Last Name", required=False)
    claim_date = forms.CharField(label="Claim Date", required=False)
    address_line_1 = forms.CharField(label="Address Line 1", required=False)
    address_line_2 = forms.CharField(label="Address Line 2", required=False)
    chk_revive = forms.BooleanField(label="Re-Vive", initial=False, required=False)
    chk_italia = forms.BooleanField(label="Natuzzi Italia", initial=False, required=False)
    chk_editions = forms.BooleanField(label="Natuzzi Editions", initial=False, required=False)
    chk_softaly = forms.BooleanField(label="Softaly", initial=False, required=False)
    model_1 = forms.CharField(label="Item 1 - Model", required=False)
    version_1 = forms.CharField(label="Item 1 - Version", required=False)
    style_1 = forms.CharField(label="Item 1 - Style", required=False)
    descr_1 = forms.CharField(label="Item 1 - Description", required=False)

    def get_data_fields_dict(self):
        pdf_fields = {}

        if self.cleaned_data:
            if self.cleaned_data['first_name']:
                pdf_fields['FirstName'] = self.cleaned_data['first_name']
            if self.cleaned_data['last_name']:
                pdf_fields['LastName'] = self.cleaned_data['last_name']
            if self.cleaned_data['claim_date']:
                pdf_fields['ClaimDate'] = self.cleaned_data['claim_date'] #formats.date_format(self.cleaned_data['claim'].claim_date, 'DATE_FORMAT_SHORT')
            if self.cleaned_data['address_line_1']:
                pdf_fields['AddressLine1'] = self.cleaned_data['address_line_1']
            if self.cleaned_data['address_line_2']:
                pdf_fields['AddressLine2'] = self.cleaned_data['address_line_2']
            if self.cleaned_data['chk_revive']:
                pdf_fields['ChkRevive'] = '1'
            if self.cleaned_data['chk_italia']:
                pdf_fields['ChkItalia'] = '1'
            if self.cleaned_data['chk_editions']:
                pdf_fields['ChkEditions'] = '1'
            if self.cleaned_data['chk_softaly']:
                pdf_fields['ChkSoftaly'] = '1'
            if self.cleaned_data['model_1']:
                pdf_fields['Model1'] = self.cleaned_data['model_1']
            if self.cleaned_data['version_1']:
                pdf_fields['Version1'] = self.cleaned_data['version_1']
            if self.cleaned_data['style_1']:
                pdf_fields['Style1'] = self.cleaned_data['style_1']
            if self.cleaned_data['descr_1']:
                pdf_fields['Description1'] = self.cleaned_data['descr_1']

        return pdf_fields

    class Meta:
        model = VendorClaimRequest
        widgets = {
            #'file': HiddenInput,
            #'data_fields': HiddenInput,
            #'claim': HiddenInput,
        }
        fields = "__all__"

#---------------------------------------------------
#   Form Sets
#---------------------------------------------------

#inline formsets
def get_claim_status_formset(extra=1, max_num=1000, request=None):
    return inlineformset_factory(Claim, ClaimStatus, form=ClaimStatusForm, fields='__all__', extra=extra, max_num=max_num, can_delete=True)

def get_claim_photos_formset(extra=1, max_num=1000, request=None):
    return inlineformset_factory(Claim, ClaimPhoto, form=ClaimPhotoForm, fields='__all__', extra=extra, max_num=max_num, can_delete=True)
 