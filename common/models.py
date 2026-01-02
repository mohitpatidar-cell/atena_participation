from django.db import models

# Create your models here.
class ProviderSummaryPDF(models.Model):
    provider_name = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to='provider_pdfs/')
    extracted_data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')  # pending / processing / done / error
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.provider_name or f"Provider PDF #{self.id}"