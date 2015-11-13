from claims.models import Claim, ClaimStatus, ClaimPhoto
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms.utils import ErrorList
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.widgets import Select
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

        self.fields['order_invoice_num'].label = "Order/invoice #"
        self.fields['order_ref'].label = "Order"
    
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

#---------------------------------------------------
#   Form Sets
#---------------------------------------------------

#inline formsets
def get_claim_status_formset(extra=1, max_num=1000, request=None):
    return inlineformset_factory(Claim, ClaimStatus, form=ClaimStatusForm, fields='__all__', extra=extra, max_num=max_num, can_delete=True)

def get_claim_photos_formset(extra=1, max_num=1000, request=None):
    return inlineformset_factory(Claim, ClaimPhoto, form=ClaimPhotoForm, fields='__all__', extra=extra, max_num=max_num, can_delete=True)
 