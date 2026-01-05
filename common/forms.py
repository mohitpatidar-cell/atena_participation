from django import forms
from .models import ProviderSummaryPDF

class ProviderSummaryUploadForm(forms.ModelForm):
    class Meta:
        model = ProviderSummaryPDF
        fields = [
            'submitter_first_name',
            'submitter_last_name', 
            'submitter_email',
            'submitter_phone',
            'submitter_ext',
            'submitter_fax',
            'provider_name',  # Optional
            'pdf_file'
        ]
        widgets = {
            'submitter_phone': forms.TextInput(attrs={'placeholder': '(123) 456-7890'}),
            'submitter_ext': forms.TextInput(attrs={'placeholder': 'Ext 123'}),
            'submitter_fax': forms.TextInput(attrs={'placeholder': '(123) 456-7890'}),
            'provider_name': forms.TextInput(attrs={'placeholder': 'Provider Name (optional)'}),
        }
