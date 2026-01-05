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
    # STEP 1: Get MANUAL submitter data from model fields
    # -----------------------------
    manual_data = {
        "submitter_first_name": obj.submitter_first_name.strip() if obj.submitter_first_name else "",
        "submitter_last_name": obj.submitter_last_name.strip() if obj.submitter_last_name else "",
        "submitter_email": obj.submitter_email.strip() if obj.submitter_email else "",
        "submitter_phone": obj.submitter_phone.strip() if obj.submitter_phone else "",
        "submitter_ext": obj.submitter_ext.strip() if obj.submitter_ext else "",
        "submitter_fax": obj.submitter_fax.strip() if obj.submitter_fax else "",
    }
    print("✅ Manual submitter data loaded!")

    # -----------------------------
    # STEP 2: Extract PDF data
    # -----------------------------
    pdf_extracted_data = {"error": "No PDF data"}
    try:
        pdf_path = obj.pdf_file.path
        pdf_extracted_data = extract_data_from_pdf_path(pdf_path)
        print("✅ PDF data extracted!")
    except Exception as extract_error:
        pdf_extracted_data = {"extraction_error": str(extract_error)}
        print(f"⚠️ PDF extraction error: {extract_error}")

    # -----------------------------
    # STEP 3: MERGE - Manual data OVERRIDES PDF data
    # -----------------------------
    merged_data = {**pdf_extracted_data, **manual_data}  # Manual wins conflicts!
    
    # Save merged data to model
    obj.extracted_data = merged_data
    obj.status = 'extracted'
    obj.save(update_fields=['extracted_data', 'status'])
    
    print("✅ MERGED data saved!")
    print(f"🔗 Final First Name: '{merged_data.get('submitter_first_name', 'N/A')}'")
    print(f"🔗 Final Provider: '{merged_data.get('Provider_Name', merged_data.get('provider_name', 'N/A'))}'")

    # -----------------------------
    # STEP 4: Run Automation with MERGED data
    # -----------------------------
    try:
        if isinstance(merged_data, dict) and 'extraction_error' not in merged_data:
            print("🚀 Starting automation with MERGED data...")
            success = start_aetna_automation(merged_data)
            if success:
                obj.status = 'automated'
                obj.save(update_fields=['status'])
                print("✅ Automation COMPLETED!")
            else:
                obj.status = 'automation_failed'
                obj.save(update_fields=['status'])
                print("❌ Automation failed")
        else:
            print("⏭️ Skipping automation - data incomplete")
            
    except Exception as auto_error:
        print(f"❌ Automation error (data safe): {auto_error}")
        obj.status = 'automation_failed'
        obj.save(update_fields=['status'])

    return obj.id
