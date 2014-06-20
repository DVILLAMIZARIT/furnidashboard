from django import forms

class OrderIssueForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    super(OrderIssueForm, self).__init__(*args, **kwargs)
    
    self.fields['status'].initial='N'
    self.fields['status'].required = True
    
