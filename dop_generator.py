import json
import os
from anthropic import Anthropic
from reference_docs import get_ead_text, get_eta_text, get_cpr_text

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """\
You are an expert in EU construction product regulation and CE marking.

Your task: Given three regulatory reference documents and a product sheet, generate a complete \
Declaration of Performance (DoP) as structured JSON.

You must extract ALL information from the provided documents. Do NOT invent or assume any values. \
Specifically:
- Read the EU-CPR 305/2011 to understand what sections a DoP must contain (Article 4-6) and \
the legal texts about conformity, responsibility, and signing.
- Read the EAD to understand which essential characteristics must be assessed and the testing \
methods / assessment criteria for each characteristic.
- Read the ETA to find the manufacturer details, the notified body, the certificate numbers, \
the AVCP system, the Technical Assessment Body, and the product-specific test results.
- Read the product sheet to identify the specific product code, its material, and its intended use.

Then cross-reference the product sheet material/type with the EAD assessment criteria to determine \
which essential characteristics get "Pass", "NPD" (No Performance Determined), or specific values. \
The EAD defines which tests apply to metallic vs. plastic components -- use that logic, not \
hardcoded rules.

## Output format
Return ONLY valid JSON (no markdown fences, no commentary) with this structure:
{
  "product_code": "...",
  "intended_use_en": "...",
  "intended_use_de": "...",
  "manufacturer": "full manufacturer name and address as found in ETA",
  "authorised_representative_en": "...",
  "authorised_representative_de": "...",
  "avcp_system": "system number from ETA",
  "eta_details": {
    "tab_name": "Technical Assessment Body name from ETA",
    "ead_ref": "EAD reference number",
    "eta_ref": "ETA reference number",
    "notified_body": "notified body name and number from ETA",
    "certificate": "certificate number from ETA"
  },
  "performance_table": [
    {
      "characteristic_en": "English name of essential characteristic",
      "characteristic_de": "German name of essential characteristic",
      "value_en": "performance value in English",
      "value_de": "performance value in German"
    }
  ],
  "conformity_text_en": "conformity statement from EU-CPR",
  "conformity_text_de": "conformity statement in German",
  "responsibility_text_en": "responsibility statement from EU-CPR",
  "responsibility_text_de": "responsibility statement in German",
  "signed_by_text_en": "signing clause in English",
  "signed_by_text_de": "signing clause in German",
  "signatories": [
    {"name": "...", "title_en": "...", "title_de": "..."}
  ],
  "place_and_date": "place and date as found in ETA",
  "original_language_note_en": "note about original language in English",
  "original_language_note_de": "note about original language in German"
}

The performance_table MUST include ALL essential characteristics from the EAD (section on \
essential characteristics / assessment methods), including the ecology/health/safety row with \
the full REACH regulation text. Derive the correct values by matching the product material \
against the EAD test requirements.
"""


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def _build_user_prompt(product_sheet_text: str) -> str:
    ead_text = _truncate(get_ead_text(), 20000)
    eta_text = _truncate(get_eta_text(), 10000)
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
Extract every field from the documents -- do not hardcode or assume anything. Return ONLY the JSON."""


def generate_dop(product_sheet_text: str) -> dict:
    """Call Claude API to generate DoP data from a product sheet.

    Returns a dict with the structured DoP fields, all derived from the
    reference documents (EAD, ETA, EU-CPR) and the product sheet.
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

    return json.loads(response_text)
