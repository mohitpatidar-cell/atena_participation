import fitz  # PyMuPDF
import json
import os
from .openai_client import client, MODEL_NAME  # new shared client


def pdf_path_to_text(path: str) -> str:
    """Extract plain text from a PDF file using PyMuPDF."""
    if not os.path.exists(path):
        return ""
    
    doc = fitz.open(path)
    texts = [page.get_text("text") for page in doc]
    doc.close()
    return "\n".join(texts)


def call_openai_for_structured_data(raw_text: str) -> dict:
    """
    Structured data extraction using OpenAI GPT model ONLY.
    """
    data: dict = {}

    prompt = f"""
    You are an information extraction engine for CAQH provider profile documents.

    Read the following text and extract ALL possible structured information
    about the provider (identifiers, contact details, addresses, licenses,
    education, training, specialties, practice locations, affiliations,
    languages, insurance plans, etc.).

    Return ONLY one valid JSON object.
    Do NOT include any explanation, comments, or markdown.
    If some information is missing, either omit that field or use "" or [].

    TEXT:
    {raw_text[:8000]}
    """

    # -------- 1. API Call --------
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a structured data extraction engine."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=2048,
        )

        response_text = response.choices[0].message.content.strip()
    except Exception as e:
        return {
            "error": f"OpenAI call failed: {e}",
            "provider_name": "",
            "caqh_id": "",
            "npi": "",
            "email": "",
            "license": "",
            "home_address": "",
            "locations": [],
            "education": "",
            "training": "",
            "specialties": "",
            "data_source": "CAQH",
            "extraction_method": "OPENAI_ONLY",
            "complete": False,
        }

    # -------- 2. Cleanup for fenced JSON --------
    if response_text.startswith("```"):
        response_text = response_text.strip("`")
        if response_text.lower().startswith("json"):
            response_text = response_text[4:].strip()

    # -------- 3. Safe JSON parse --------
    try:
        data = json.loads(response_text)
    except Exception:
        data = {
            "provider_name": "",
            "caqh_id": "",
            "npi": "",
            "email": "",
            "license": "",
            "home_address": "",
            "locations": [],
            "education": "",
            "training": "",
            "specialties": "",
            "data_source": "CAQH",
            "extraction_method": "OPENAI_ONLY",
            "complete": False,
            "raw_parse_error": True,
        }

    # -------- 4. Ensure keys exist --------
    defaults = {
        "provider_name": "",
        "caqh_id": "",
        "npi": "",
        "email": "",
        "license": "",
        "home_address": "",
        "locations": [],
        "education": "",
        "training": "",
        "specialties": "",
        "data_source": "CAQH",
        "extraction_method": "OPENAI_ONLY",
        "complete": False,
    }

    for k, v in defaults.items():
        data.setdefault(k, v)

    # -------- 5. Complete field --------
    try:
        locations = data.get("locations") or []
        data["complete"] = bool(isinstance(locations, list) and len(locations) > 0)
    except Exception:
        data["complete"] = False

    return data


def extract_data_from_pdf_path(path: str) -> dict:
    """Complete pipeline: PDF -> Text -> Structured JSON via OpenAI API."""
    if not os.path.exists(path):
        return {"error": "PDF file not found"}

    text = pdf_path_to_text(path)
    print(f"[DEBUG] PDF TEXT LENGTH: {len(text)}")

    if len(text.strip()) < 50:
        return {"error": "No text extracted from PDF"}

    data = call_openai_for_structured_data(text)
    print("[DEBUG] FINAL DATA:", json.dumps(data, indent=2))
    return data
