import json
import os
from anthropic import Anthropic
from reference_docs import get_ead_text, get_eta_text, get_cpr_text

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """\
You are an expert in EU construction product regulation and CE marking.

Your task: Given three regulatory reference documents and a product sheet, generate a complete \
Declaration of Performance (DoP) as structured JSON.

## Where to find what

### EU-CPR 305/2011 (Construction Products Regulation)
- Article 4-6 defines what a DoP must contain: the 7 mandatory sections.
- Article 6 specifies the conformity and responsibility statements.
- The DoP must be in the language required by the member state. We need EN + DE.

### EAD 030351-00-0402 (European Assessment Document)
- IMPORTANT: This EAD covers "Mechanical fasteners for use in roofing". The DoP is about the \
FASTENER product only, NOT about the entire roofing system. Only include characteristics that \
relate to the fastener itself (e.g. tensile load, unwinding, corrosion, brittleness, fire \
performance of the fastener, ecology). Do NOT include characteristics that describe the \
waterproofing membrane/sheet itself (e.g. peel resistance of sheets, shear resistance of joints, \
water vapour permeability, dimensional stability, thickness, slipperiness, etc.).
- Section 2.2 / Chapter 2 lists essential characteristics. Extract only those that apply to the \
fastener component. The characteristic names should match how they appear in the EAD.
- The assessment methods (Chapters A.2.x in the Annex) define how each characteristic is tested \
and what constitutes a pass. Use these to determine performance values.
- The EAD distinguishes tests for metallic components vs. plastic components -- which tests apply \
depends on the product material.
- "NPD" (No Performance Determined) is used when a test does not apply to a product type.
- Performance values should be concise (e.g. "Pass", "NPD", a short result summary) -- not full \
paragraphs copied from the ETA.

### ETA-23/0859 (European Technical Assessment)
- Contains the manufacturer name and address.
- Lists the AVCP system number.
- Names the Technical Assessment Body (TAB) that issued the ETA -- use only the short name.
- Names the notified body for factory production control -- this is a DIFFERENT entity than the TAB. \
Look for sections about "factory production control", "Überwachung der werkseigenen \
Produktionskontrolle", or "AVCP". The notified body has a 4-digit body number. It is always \
present for AVCP system 2+ products.
- Contains the certificate number for factory production control -- look near the notified body \
information. This is NOT the ETA reference number itself.
- Contains the intended use description.
- Contains the authorised representative status.
- Contains the REACH / ecology statement text.
- Contains the original language information.

### Product Sheet
- Contains the specific product code.
- Contains the material description, which determines product type and which EAD tests apply.

## Performance values: style guide
- Keep values SHORT and standardized: "Pass", "NPD", a class designation, or a brief measured result.
- Do NOT copy long paragraphs from the ETA as performance values.
- Reference annexes where appropriate (e.g. for tensile loading, refer to the ETA annex).
- For characteristics that don't apply to the product type, use "NPD".

## Output format
Return ONLY valid JSON (no markdown fences, no commentary):
{
  "product_code": "from product sheet",
  "intended_use_en": "from ETA",
  "intended_use_de": "German translation of intended use",
  "manufacturer": "name and address from ETA",
  "authorised_representative_en": "from ETA",
  "authorised_representative_de": "German version",
  "avcp_system": "from ETA",
  "eta_details": {
    "tab_name": "short TAB name from ETA",
    "ead_ref": "EAD reference number from ETA",
    "eta_ref": "ETA reference number",
    "notified_body": "notified body for factory production control (NOT the TAB)",
    "certificate": "certificate number for factory production control (NOT the ETA number)"
  },
  "performance_table": [
    {"characteristic_en": "from EAD", "characteristic_de": "from EAD", "value_en": "...", "value_de": "..."}
  ],
  "conformity_text_en": "from EU-CPR Article 6",
  "conformity_text_de": "German version",
  "responsibility_text_en": "from EU-CPR Article 6",
  "responsibility_text_de": "German version",
  "signed_by_text_en": "signing clause",
  "signed_by_text_de": "German version",
  "original_language_note_en": "from ETA",
  "original_language_note_de": "German version"
}

The performance_table must include ALL essential characteristics from the EAD section on assessment \
methods, plus the ecology/REACH row with the full text from the ETA.
"""


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def _build_user_prompt(product_sheet_text: str) -> str:
    ead_text = _truncate(get_ead_text(), 25000)
    eta_text = _truncate(get_eta_text(), 15000)
    cpr_text = _truncate(get_cpr_text(), 15000)

    return f"""## Reference Document 1: EU-CPR 305/2011 (Construction Products Regulation)
{cpr_text}

## Reference Document 2: EAD 030351-00-0402 (European Assessment Document)
{ead_text}

## Reference Document 3: ETA-23/0859 (European Technical Assessment)
{eta_text}

## Product Sheet
{product_sheet_text}

Based on ALL three reference documents and the product sheet, generate the complete DoP JSON. \
Extract all values from the documents. Return ONLY the JSON."""


def generate_dop(product_sheet_text: str, signatories: list[dict] = None,
                 place_and_date: str = None, notified_body: dict = None,
                 certificate: str = None) -> dict:
    """Call Claude API to generate DoP data from a product sheet.

    signatories, place_and_date, notified_body, and certificate are
    provided by the user via UI and override LLM-derived values.
    """
    user_prompt = _build_user_prompt(product_sheet_text)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    response_text = message.content[0].text.strip()

    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        response_text = "\n".join(lines)

    dop_data = json.loads(response_text)

    if signatories:
        dop_data["signatories"] = signatories
    if place_and_date:
        dop_data["place_and_date"] = place_and_date
    if notified_body:
        eta = dop_data.setdefault("eta_details", {})
        eta["notified_body"] = f"{notified_body['name']}, {notified_body['number']}"
    if certificate:
        eta = dop_data.setdefault("eta_details", {})
        eta["certificate"] = certificate

    return dop_data
