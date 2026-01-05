from django.db import models

# Updated SINGLE Model - All fields in ProviderSummaryPDF
class ProviderSummaryPDF(models.Model):
    # ✅ MANUAL Submitter Fields (Form se fill honge)
    submitter_first_name = models.CharField(max_length=100, blank=True)
    submitter_last_name = models.CharField(max_length=100, blank=True)
    submitter_email = models.EmailField(blank=True)
    submitter_phone = models.CharField(max_length=20, blank=True)
    submitter_ext = models.CharField(max_length=10, blank=True)
    submitter_fax = models.CharField(max_length=20, blank=True)
    
    # ✅ Existing Provider Fields
    provider_name = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to='provider_pdfs/')
    extracted_data = models.JSONField(blank=True, null=True)  # MERGED final data
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.submitter_first_name} {self.submitter_last_name} - {self.provider_name or 'PDF'}"

    def get_merged_data(self):
        """Returns merged manual + extracted data for automation"""
        manual_data = {
            "submitter_first_name": self.submitter_first_name,
            "submitter_last_name": self.submitter_last_name,
            "submitter_email": self.submitter_email,
            "submitter_phone": self.submitter_phone,
            "submitter_ext": self.submitter_ext,
            "submitter_fax": self.submitter_fax,
        }
        
        extracted = self.extracted_data or {}
        return {**extracted, **manual_data}  # Manual OVERRIDES extracted!
