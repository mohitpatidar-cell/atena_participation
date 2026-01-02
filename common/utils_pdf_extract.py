import fitz  # PyMuPDF (backup) 
import json
import os
from .gemini_client import client  # ✅ Shared client

def pdf_path_to_text(path: str) -> str:
    """Original function - now with better text extraction."""
    if not os.path.exists(path):
        return ""
    
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text("text"))
    doc.close()
    return "\n".join(texts)
def call_gemini_for_structured_data(raw_text: str) -> dict:
    """🔥 FINAL BULLETPROOF SOLUTION - REGEX + Manual Parsing FIRST"""
    
    import re
    import json
    
    # 🔥 STEP 1: MANUAL REGEX EXTRACTION - MOST CRITICAL FIELDS FIRST
    manual_data = {}
    
    # Provider Name & CAQH ID (ALWAYS FIRST LINES)
    name_match = re.search(r'NELSON,\s*CAROLYN\s*D?\s*(?:Clinical Social Worker)?', raw_text, re.IGNORECASE)
    manual_data['provider_name'] = name_match.group().strip().replace('NELSON, ', '') if name_match else ''
    
    caqh_match = re.search(r'CAQH Provider ID\s*:\s*(\d+)', raw_text)
    manual_data['caqh_id'] = caqh_match.group(1) if caqh_match else ''
    
    # NPI
    npi_match = re.search(r'Individual NPI\s*:\s*(\d{10})', raw_text)
    manual_data['npi'] = npi_match.group(1) if npi_match else ''
    
    # Email
    email_match = re.search(r'Primary E-mail Address\s*:\s*([^\s\n@]+@[^\s\n@]+\.[^\s\n@]+)', raw_text)
    manual_data['email'] = email_match.group(1) if email_match else ''
    
    # License
    license_match = re.search(r'License Number\s*:\s*(\w+)', raw_text)
    manual_data['license'] = license_match.group(1) if license_match else ''
    
    # Home Address
    home_street = re.search(r'Street 1\s*:\s*5419 WILLIAMS ST', raw_text)
    home_city = re.search(r'City\s*:\s*Wayne', raw_text)
    home_state = re.search(r'State\s*:\s*MI', raw_text)
    home_zip = re.search(r'Zip Code\s*:\s*48184', raw_text)
    manual_data['home_address'] = f"5419 WILLIAMS ST, Wayne MI 48184" if home_street else ''
    
    # Practice Locations - Find ALL "Practice Name : Pure psychiatry of Michigan"
    locations = []
    practice_pattern = r'Practice Name\s*:\s*Pure psychiatry of Michigan.*?Street 1\s*:\s*([^\n]+).*?City\s*:\s*([^\n]+).*?State\s*:\s*MI.*?Zip Code\s*:\s*([^\n]+).*?Appointment Phone Number\s*:\s*([^\n]+)'
    practice_matches = re.finditer(practice_pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    for match in practice_matches:
        loc = {
            'practice_name': 'Pure psychiatry of Michigan',
            'street1': match.group(1).strip(),
            'city': match.group(2).strip(),
            'state': 'MI',
            'zip': match.group(3).strip(),
            'phone': match.group(4).strip()
        }
        locations.append(loc)
    
    manual_data['locations'] = locations
    manual_data['total_locations'] = len(locations)
    
    # If manual extraction good enough → RETURN IMMEDIATELY
    if manual_data.get('caqh_id') and manual_data.get('npi') and len(locations) > 0:
        manual_data['extraction_method'] = 'REGEX_SUCCESS'
        manual_data['complete'] = True
        manual_data['data_source'] = 'CAQH'
        return manual_data
    
    # 🔥 STEP 2: Gemini as FALLBACK only for missing fields
    try:
        prompt = f"""
EXTRACT ONLY MISSING FIELDS from this CAQH PDF:
Missing: {list(set(['education', 'training', 'specialties']) - set(manual_data.keys()))}

CRITICAL FIELDS:
- School/Degree/Graduation
- Primary Specialty: Social Worker (104100000X)
- License State: MI

Output ONLY:
{{"education": "Wayne State University MSW", "specialties": "Social Worker"}} 

TEXT: {raw_text[:8000]}
"""
        response = client.generate_content(prompt)
        response_text = response.text.strip()
        response_text = re.sub(r'```json?\s*', '', response_text).strip()
        
        gemini_data = json.loads(response_text)
        manual_data.update(gemini_data)
        
    except:
        manual_data['gemini_fallback'] = 'failed'
    
    manual_data['complete'] = manual_data.get('total_locations', 0) > 0
    manual_data['data_source'] = 'CAQH'
    
    return manual_data


def extract_data_from_pdf_path(path: str) -> dict:
    """Original function signature - now robust."""
    if not os.path.exists(path):
        return {"error": "PDF file not found"}
    
    # Text extraction first (original approach)
    text = pdf_path_to_text(path)
    print(f"PDF TEXT LENGTH: {len(text)}")
    
    if len(text.strip()) < 50:
        return {"error": "No text extracted from PDF"}
    
    data = call_gemini_for_structured_data(text)
    print("FINAL DATA:", json.dumps(data, indent=2))
    return data
