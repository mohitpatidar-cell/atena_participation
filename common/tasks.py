from celery import shared_task
from django.db import transaction
from .models import ProviderSummaryPDF
from .utils_pdf_extract import extract_data_from_pdf_path

# Import the automation function
from .automation import start_aetna_automation
@shared_task
def process_provider_pdf(provider_pdf_id):
    obj = ProviderSummaryPDF.objects.get(id=provider_pdf_id)
    obj.status = 'processing'
    obj.save(update_fields=['status'])

    # -----------------------------
    # ALWAYS save extracted data first
    # -----------------------------
    extracted_data = {"error": "No data extracted"}
    
    try:
        pdf_path = obj.pdf_file.path
        extracted_data = extract_data_from_pdf_path(pdf_path)  # Success ya error dict milega
        
        # ✅ DATA SAVED - success ho ya error ho
        obj.extracted_data = extracted_data
        obj.status = 'extracted'  # ✅ New status for data extracted
        obj.save(update_fields=['extracted_data', 'status'])
        
        print("✅ Data saved successfully!")
        print(f"Extracted: {extracted_data.get('provider_name', 'No name')}")

    except Exception as extract_error:
        # ✅ Even extraction fails, save error data
        extracted_data = {"extraction_error": str(extract_error)}
        obj.extracted_data = extracted_data
        obj.status = 'extracted'  # Same status
        obj.save(update_fields=['extracted_data', 'status'])
        print(f"❌ Extraction error (but data saved): {extract_error}")

    # -----------------------------
    # Automation - separate try block
    # -----------------------------
    try:
        if isinstance(extracted_data, dict) and 'error' not in extracted_data:
            print("🚀 Starting automation...")
            success = start_aetna_automation(extracted_data)
            if success:
                obj.status = 'automated'
                obj.save(update_fields=['status'])
                print("✅ Automation completed!")
            else:
                obj.status = 'automation_failed'
                obj.save(update_fields=['status'])
                print("❌ Automation failed")
        else:
            print("⏭️ Skipping automation - data extraction incomplete")
            
    except Exception as auto_error:
        # ✅ Automation fail ho to bhi data safe hai
        print(f"❌ Automation error (data safe): {auto_error}")
        obj.status = 'automation_failed'
        obj.save(update_fields=['status'])

    return obj.id
