from django import forms
from .models import ProviderSummaryPDF

class ProviderSummaryUploadForm(forms.ModelForm):
    class Meta:
        model = ProviderSummaryPDF
        fields = ['provider_name', 'pdf_file']
