from django.forms import HiddenInput
from django.utils import formats

from claims.models import Claim, ClaimStatus, ClaimPhoto, VendorClaimRequest
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from bootstrap3_datetime.widgets import DateTimePicker
from ajax_select.fields import AutoCompleteSelectField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field, HTML, Hidden
from crispy_forms.bootstrap import AppendedText, InlineRadios, InlineField

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

    reference_no = forms.CharField(label="Reference #", required=False)
    first_name = forms.CharField(label="Customer First Name", required=False)
    last_name = forms.CharField(label="Customer Last Name", required=False)
    claim_date = forms.CharField(label="Claim Date", required=False)
    address_line_1 = forms.CharField(label="Address Line 1", required=False)
    address_line_2 = forms.CharField(label="Address Line 2 (City/State/ZIP)", required=False)
    phone_num_home = forms.CharField(label="Phone number (home)", required=False)
    phone_num_work = forms.CharField(label="Phone number (work)", required=False)
    email = forms.EmailField(label="E-mail", required=False)
    chk_editions = forms.BooleanField(label="Natuzzi Editions", initial=False, required=False)
    chk_revive = forms.BooleanField(label="Re-Vive", initial=False, required=False)
    chk_softaly = forms.BooleanField(label="Softaly", initial=False, required=False)
    chk_italia = forms.BooleanField(label="Natuzzi Italia", initial=False, required=False)

    model_1 = forms.CharField(label="Item 1 - Model", required=False)
    version_1 = forms.CharField(label="Item 1 - Version", required=False)
    style_1 = forms.CharField(label="Item 1 - Style", required=False)
    leather_fabric_1 = forms.CharField(label="Leather/Fabric #", required=False)
    id_num_1 = forms.CharField(label="ID Number", required=False)

    model_2 = forms.CharField(label="Item 2 - Model", required=False)
    version_2 = forms.CharField(label="Item 2 - Version", required=False)
    style_2 = forms.CharField(label="Item 2 - Style", required=False)
    leather_fabric_2 = forms.CharField(label="Leather/Fabric #", required=False)
    id_num_2 = forms.CharField(label="ID Number", required=False)

    model_3 = forms.CharField(label="Item 3 - Model", required=False)
    version_3 = forms.CharField(label="Item 3 - Version", required=False)
    style_3 = forms.CharField(label="Item 3 - Style", required=False)
    leather_fabric_3 = forms.CharField(label="Leather/Fabric #", required=False)
    id_num_3 = forms.CharField(label="ID Number", required=False)

    model_4 = forms.CharField(label="Item 4 - Model", required=False)
    version_4 = forms.CharField(label="Item 4 - Version", required=False)
    style_4 = forms.CharField(label="Item 4 - Style", required=False)
    leather_fabric_4 = forms.CharField(label="Leather/Fabric #", required=False)
    id_num_4 = forms.CharField(label="ID Number", required=False)

    delivery_date = forms.CharField(label="Delivery Date", required=False)

    descr_1 = forms.CharField(label="Item 1 - Description", required=False)
    warranty_1 = forms.CharField(label="Warranty Info", required=False)
    parts_1 = forms.CharField(label="Part", required=False)
    labor_1 = forms.CharField(label="Labor", required=False)

    descr_2 = forms.CharField(label="Item 2 - Description", required=False)
    warranty_2 = forms.CharField(label="Warranty Info", required=False)
    parts_2 = forms.CharField(label="Part", required=False)
    labor_2 = forms.CharField(label="Labor", required=False)

    descr_3 = forms.CharField(label="Item 3 - Description", required=False)
    warranty_3 = forms.CharField(label="Warranty Info", required=False)
    parts_3 = forms.CharField(label="Part", required=False)
    labor_3 = forms.CharField(label="Labor", required=False)

    descr_4 = forms.CharField(label="Item 4 - Description", required=False)
    warranty_4 = forms.CharField(label="Warranty Info", required=False)
    parts_4 = forms.CharField(label="Part", required=False)
    labor_4 = forms.CharField(label="Labor", required=False)

    descr_5 = forms.CharField(label="Item 5 - Description", required=False)
    warranty_5 = forms.CharField(label="Warranty Info", required=False)
    parts_5 = forms.CharField(label="Part", required=False)
    labor_5 = forms.CharField(label="Labor", required=False)

    def get_data_fields_dict(self):
        pdf_fields = {}

        if self.cleaned_data:
            pdf_fields['ClaimDate'] = self.cleaned_data.get('claim_date', '')
            pdf_fields['RefInfo'] = self.cleaned_data.get('reference_no', '')
            pdf_fields['FirstName'] = self.cleaned_dataget('first_name', '')
            pdf_fields['LastName'] = self.cleaned_data.get('last_name', '')
            pdf_fields['AddressLine1'] = self.cleaned_data.get('address_line_1', '')
            pdf_fields['AddressLine2'] = self.cleaned_data.get('address_line_2', '')
            pdf_fields['PhoneNumPhone'] = self.cleaned_data.get('phone_num_home', '')
            pdf_fields['PhoneNumWork'] = self.cleaned_data.get('phone_num_work', '')
            pdf_fields['Email'] = self.cleaned_data.get('email', '')

            if self.cleaned_data['chk_revive']:
                pdf_fields['ChkRevive'] = 1
            if self.cleaned_data['chk_italia']:
                pdf_fields['ChkItalia'] = 1
            if self.cleaned_data['chk_editions']:
                pdf_fields['ChkEditions'] = 1
            if self.cleaned_data['chk_softaly']:
                pdf_fields['ChkSoftaly'] = 1

            pdf_fields['Model1'] = self.cleaned_data.get('model_1', '')
            pdf_fields['Model2'] = self.cleaned_data.get('model_2', '')
            pdf_fields['Model3'] = self.cleaned_data.get('model_3', '')
            pdf_fields['Model4'] = self.cleaned_data.get('model_4', '')
            pdf_fields['Version1'] = self.cleaned_data.get('version_1', '')
            pdf_fields['Version2'] = self.cleaned_data.get('version_2', '')
            pdf_fields['Version3'] = self.cleaned_data.get('version_3', '')
            pdf_fields['Version4'] = self.cleaned_data.get('version_4', '')
            pdf_fields['Style1'] = self.cleaned_data.get('style_1', '')
            pdf_fields['Style2'] = self.cleaned_data.get('style_2', '')
            pdf_fields['Style3'] = self.cleaned_data.get('style_3', '')
            pdf_fields['Style4'] = self.cleaned_data.get('style_4', '')
            pdf_fields['LeatherFabric1'] = self.cleaned_data.get('leather_fabric_1', '')
            pdf_fields['LeatherFabric2'] = self.cleaned_data.get('leather_fabric_2', '')
            pdf_fields['LeatherFabric3'] = self.cleaned_data.get('leather_fabric_3', '')
            pdf_fields['LeatherFabric4'] = self.cleaned_data.get('leather_fabric_4', '')
            pdf_fields['IdNum1'] = self.cleaned_data.get('id_num_1', '')
            pdf_fields['IdNum2'] = self.cleaned_data.get('id_num_2', '')
            pdf_fields['IdNum3'] = self.cleaned_data.get('id_num_3', '')
            pdf_fields['IdNum4'] = self.cleaned_data.get('id_num_4', '')

            pdf_fields['DeliveryDate'] = self.cleaned_data.get('delivery_date', '')

            pdf_fields['Description1'] = self.cleaned_data.get('descr_1', '')
            pdf_fields['Description2'] = self.cleaned_data.get('descr_2', '')
            pdf_fields['Description3'] = self.cleaned_data.get('descr_3', '')
            pdf_fields['Description4'] = self.cleaned_data.get('descr_4', '')
            pdf_fields['Description5'] = self.cleaned_data.get('descr_5', '')
            pdf_fields['Warranty1'] = self.cleaned_data.get('warranty_1', '')
            pdf_fields['Warranty2'] = self.cleaned_data.get('warranty_2', '')
            pdf_fields['Warranty3'] = self.cleaned_data.get('warranty_3', '')
            pdf_fields['Warranty4'] = self.cleaned_data.get('warranty_4', '')
            pdf_fields['Warranty5'] = self.cleaned_data.get('warranty_5', '')
            pdf_fields['PartsRow1'] = self.cleaned_data.get('parts_1', '')
            pdf_fields['PartsRow2'] = self.cleaned_data.get('parts_2', '')
            pdf_fields['PartsRow3'] = self.cleaned_data.get('parts_3', '')
            pdf_fields['PartsRow4'] = self.cleaned_data.get('parts_4', '')
            pdf_fields['PartsRow5'] = self.cleaned_data.get('parts_5', '')
            pdf_fields['LaborRow1'] = self.cleaned_data.get('labor_1', '')
            pdf_fields['LaborRow2'] = self.cleaned_data.get('labor_2', '')
            pdf_fields['LaborRow3'] = self.cleaned_data.get('labor_3', '')
            pdf_fields['LaborRow4'] = self.cleaned_data.get('labor_4', '')
            pdf_fields['LaborRow5'] = self.cleaned_data.get('labor_5', '')


        return pdf_fields

    def __init__(self, *args, **kwargs):
        super(NatuzziClaimVendorRequestForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.form_tag = False
        self.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                'Natuzzi Claim Request Form',
                Div(
                    Field('claim_date', wrapper_class='field-wrapper col-md-2 pull-left'),
                    Field('reference_no', wrapper_class='field-wrapper col-md-2 pull-left'),
                    css_class='row'
                ),
                Div(
                    Field('first_name', wrapper_class='field-wrapper col-md-2'),
                    Field('last_name', wrapper_class='field-wrapper col-md-2'),
                    css_class='row'
                ),
                Div(
                    Field('address_line_1', wrapper_class='field-wrapper col-md-4'),
                    Field('address_line_2', wrapper_class='field-wrapper col-md-4'),
                    css_class='row',
                ),
                Div(
                    Field('phone_num_home', wrapper_class='field-wrapper col-md-2'),
                    Field('phone_num_work', wrapper_class='field-wrapper col-md-2'),
                    Field('email', wrapper_class='field-wrapper col-md-2'),
                    css_class='row',
                ),
                HTML('<hr/>'),
                Div(
                    HTML('<h4>Select Item Brand</h4>'),
                    InlineField('chk_editions', wrapper_class='col-md-2 checkbox-inline', template='partial/inline_field.html'),
                    InlineField('chk_revive', wrapper_class='col-md-2 checkbox-inline', template='partial/inline_field.html'),
                    InlineField('chk_softaly', wrapper_class='col-md-2 checkbox-inline', template='partial/inline_field.html'),
                    InlineField('chk_italia', wrapper_class='col-md-2 checkbox-inline', template='partial/inline_field.html'),
                    css_class="row checkbox"
                ),
                HTML('<hr/>'),
                Div(
                    HTML('<h4 class="col-md-3">Model</h4> '),
                    HTML('<h4 class="col-md-2">Version</h4> '),
                    HTML('<h4 class="col-md-2">Style</h4> '),
                    HTML('<h4 class="col-md-2">Leather/Fabric #</h4> '),
                    HTML('<h4 class="col-md-2">ID Number</h4>'),
                    css_class='row',
                ),
                Div(
                    Field('model_1', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('version_1', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('style_1', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('leather_fabric_1', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('id_num_1', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    css_class="row"
                ),
                Div(
                    Field('model_2', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('version_2', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('style_2', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('leather_fabric_2', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('id_num_2', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    css_class="row"
                ),
                Div(
                    Field('model_3', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('version_3', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('style_3', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('leather_fabric_3', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('id_num_3', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    css_class="row"
                ),
                Div(
                    Field('model_4', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('version_4', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('style_4', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('leather_fabric_4', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    Field('id_num_4', wrapper_class='col-md-2', template='partial/inline_field.html'),
                    css_class="row"
                ),
                Div(
                    Field('delivery_date', wrapper_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<h4 class="col-md-6">Description of Product Issue</h4> '),
                    HTML('<h4 class="col-md-3">Warranty That Applies</h4> '),
                    HTML('<h4 class="col-md-1">Parts</h4> '),
                    HTML('<h4 class="col-md-1">Labor</h4> '),
                    css_class='row',
                ),
                Div(
                    Field('descr_1', wrapper_class='col-md-6', template='partial/inline_field.html'),
                    Field('warranty_1', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('parts_1', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    Field('labor_1', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    css_class='row',
                ),
                Div(
                    Field('descr_2', wrapper_class='col-md-6', template='partial/inline_field.html'),
                    Field('warranty_2', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('parts_2', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    Field('labor_2', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    css_class='row',
                ),
                Div(
                    Field('descr_3', wrapper_class='col-md-6', template='partial/inline_field.html'),
                    Field('warranty_3', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('parts_3', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    Field('labor_3', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    css_class='row',
                ),
                Div(
                    Field('descr_4', wrapper_class='col-md-6', template='partial/inline_field.html'),
                    Field('warranty_4', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('parts_4', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    Field('labor_4', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    css_class='row',
                ),
                Div(
                    Field('descr_5', wrapper_class='col-md-6', template='partial/inline_field.html'),
                    Field('warranty_5', wrapper_class='col-md-3', template='partial/inline_field.html'),
                    Field('parts_5', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    Field('labor_5', wrapper_class='col-md-1', template='partial/inline_field.html'),
                    css_class='row',
                ),
                Field('file'),
                Field('claim_fields'),
                Field('claim'),
                Submit('submit', 'Create Claim', css_class='btn btn-primary btn-large'),
            )
        )

    class Meta:
        model = VendorClaimRequest
        widgets = {
            'file': HiddenInput,
            'data_fields': HiddenInput,
            'claim': HiddenInput,
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
 