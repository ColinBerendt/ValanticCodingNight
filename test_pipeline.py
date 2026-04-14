"""End-to-end test: extract product sheet -> LLM generates DoP -> PDF output."""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from pdf_extractor import extract_text
from dop_generator import generate_dop
from pdf_builder import build_dop_pdf

CASE_DIR = os.path.join(os.path.dirname(__file__), "Case 1 SFS - Automated CE Marking")


def test_product(name: str, filename: str):
    print(f"\n{'='*60}")
    print(f"Testing: {name} ({filename})")
    print(f"{'='*60}")

    product_text = extract_text(os.path.join(CASE_DIR, filename))
    print(f"Extracted {len(product_text)} chars from product sheet")

    print("Calling Claude API (no solution files, no hardcoded rules)...")
    dop_data = generate_dop(product_text)

    # Save raw JSON for inspection
    json_path = os.path.join(os.path.dirname(__file__), f"dop_{dop_data['product_code']}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dop_data, f, indent=2, ensure_ascii=False)
    print(f"Raw JSON saved: {json_path}")

    # Print key fields
    print(f"  Product code: {dop_data['product_code']}")
    print(f"  Manufacturer: {dop_data.get('manufacturer', 'MISSING')}")
    print(f"  AVCP: {dop_data.get('avcp_system', 'MISSING')}")
    eta = dop_data.get("eta_details", {})
    print(f"  TAB: {eta.get('tab_name', 'MISSING')}")
    print(f"  ETA ref: {eta.get('eta_ref', 'MISSING')}")
    print(f"  Notified body: {eta.get('notified_body', 'MISSING')}")
    print(f"  Certificate: {eta.get('certificate', 'MISSING')}")
    print(f"  Performance rows: {len(dop_data.get('performance_table', []))}")
    for row in dop_data.get("performance_table", []):
        text = f"    {row.get('characteristic_en','')}: {row.get('value_en','')}"
        print(text.encode("ascii", errors="replace").decode("ascii"))
    print(f"  Signatories: {dop_data.get('signatories', 'MISSING')}")

    # Generate PDF
    pdf_bytes = build_dop_pdf(dop_data)
    out_path = os.path.join(os.path.dirname(__file__), f"DoP_{dop_data['product_code']}.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  DoP PDF: {out_path} ({len(pdf_bytes)} bytes)")


if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set. Create a .env file or set the env var.")
    exit(1)

test_product("BS-4,8 (carbon steel screw)", "Product Sheet BS-48.pdf")
test_product("RP50n (plastic sleeve)", "Product Sheet RP50n.pdf")

print("\nDone!")
