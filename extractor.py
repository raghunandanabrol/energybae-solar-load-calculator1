
import groq
import base64
import json
import pdfplumber
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()


def pdf_to_base64(pdf_bytes: bytes) -> str:
    """Convert first page of PDF to base64 image"""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page = pdf.pages[0]
        img  = page.to_image(resolution=200).original
        buf  = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image file to base64"""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# Instruction we give to Groq AI
EXTRACTION_PROMPT = """
You are an expert electricity bill reader for Indian utility bills
like MSEDCL, BESCOM, TATA Power, Adani Electricity.

Look at this electricity bill image very carefully.
Extract ALL of the following fields from this bill.
Return ONLY a valid JSON object.
No explanation. No markdown. Just pure JSON.

{
  "consumer_name": "Full name of consumer or null",
  "consumer_number": "Consumer account number or null",
  "meter_number": "Meter number or null",
  "billing_address": "Full address or null",
  "billing_month": "Month and year like March 2024 or null",
  "billing_period_from": "Start date DD/MM/YYYY or null",
  "billing_period_to": "End date DD/MM/YYYY or null",
  "tariff_category": "Tariff type like LT-1 Residential or null",
  "sanctioned_load_kw": "number only like 5.0 or null",
  "contract_demand_kva": "number only or null",
  "units_consumed_kwh": "number only like 320 or null",
  "previous_reading": "number only or null",
  "current_reading": "number only or null",
  "number_of_days": "number only like 30 or null",
  "total_bill_amount": "number only like 3200 or null",
  "energy_charges": "number only or null",
  "fixed_charges": "number only or null",
  "tax_amount": "number only or null",
  "power_factor": "number only or null",
  "distribution_company": "company name like MSEDCL or null",
  "phase_type": "Single Phase or Three Phase or null",
  "monthly_avg_units": "number only or null"
}

Very Important Rules:
- Write null if field not found in bill
- Numeric fields must have numbers only
- No Rs symbol no kWh text just the number
- Be very accurate used for solar calculations
"""

# Groq vision models to try in order
GROQ_VISION_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "llama-3.2-90b-vision-preview",
    "llama-3.2-11b-vision-preview",
]


def get_groq_client():
    """Create Groq client with API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Groq API key not found! "
            "Please enter your Groq API key in the sidebar. "
            "Get free key from: console.groq.com"
        )

    return groq.Groq(api_key=api_key)


def call_groq_with_fallback(client, b64_image):
    """Try each Groq model one by one until one works"""
    last_error = None

    for model_name in GROQ_VISION_MODELS:
        try:
            print(f"Trying model: {model_name}")

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": EXTRACTION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            print(f"Success with model: {model_name}")
            return result

        except Exception as e:
            print(f"Model {model_name} failed: {str(e)}")
            last_error = e
            continue

    raise ValueError(
        f"All Groq models failed. "
        f"Last error: {str(last_error)} "
        f"Please check your API key at console.groq.com"
    )


def clean_json_text(raw_text):
    """Clean up AI response to get pure JSON"""

    # Remove markdown code blocks if present
    if "```" in raw_text:
        parts    = raw_text.split("```")
        raw_text = parts[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    # Find JSON object start and end
    start = raw_text.find("{")
    end   = raw_text.rfind("}") + 1

    if start != -1 and end > start:
        raw_text = raw_text[start:end]

    return raw_text.strip()


def extract_bill_data(file_bytes, file_type):
    """
    Main extraction function using Groq

    file_bytes : raw file content
    file_type  : 'pdf' or 'image'
    Returns    : dictionary with all bill fields
    """

    # Step 1: Convert file to base64
    if file_type == "pdf":
        b64_image = pdf_to_base64(file_bytes)
    else:
        b64_image = image_to_base64(file_bytes)

    # Step 2: Create Groq client
    client = get_groq_client()

    # Step 3: Send to Groq with fallback models
    raw_text = call_groq_with_fallback(client, b64_image)

    # Step 4: Clean up the response
    clean_text = clean_json_text(raw_text)

    # Step 5: Convert to Python dictionary
    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Could not parse AI response as JSON. "
            f"Error: {e}. "
            f"Raw response was: {raw_text}"
        )

    # Step 6: Make sure all required keys exist
    required_keys = [
        "consumer_name",
        "consumer_number",
        "meter_number",
        "billing_address",
        "billing_month",
        "billing_period_from",
        "billing_period_to",
        "tariff_category",
        "sanctioned_load_kw",
        "contract_demand_kva",
        "units_consumed_kwh",
        "previous_reading",
        "current_reading",
        "number_of_days",
        "total_bill_amount",
        "energy_charges",
        "fixed_charges",
        "tax_amount",
        "power_factor",
        "distribution_company",
        "phase_type",
        "monthly_avg_units"
    ]

    for key in required_keys:
        if key not in data:
            data[key] = None

    return data