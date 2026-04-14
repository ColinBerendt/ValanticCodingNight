import os
from fpdf import FPDF

FONT_DIR = os.path.join(os.path.dirname(__file__), "static")
_FONT = "DejaVu"


class DoPPDF(FPDF):
    def __init__(self, product_code: str):
        super().__init__()
        self.product_code = product_code
        self.set_auto_page_break(auto=True, margin=25)
        self.add_font(_FONT, "", os.path.join(FONT_DIR, "DejaVuSans.ttf"), uni=True)
        self.add_font(_FONT, "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), uni=True)
        self.add_font(_FONT, "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"), uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font(_FONT, "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, f"DoP {self.product_code}", align="L")
            self.cell(0, 5, f"{self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(3)

    def section_heading(self, number: str, text: str):
        self.set_font(_FONT, "B", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, f"{number}. {text}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def section_value(self, text: str):
        self.set_font(_FONT, "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def add_performance_table(self, rows: list[dict], char_key: str, val_key: str,
                              header_char: str, header_val: str):
        col_w = [100, 80]
        self.set_font(_FONT, "B", 9)
        self.set_fill_color(230, 235, 245)
        self.cell(col_w[0], 7, header_char, border=1, fill=True)
        self.cell(col_w[1], 7, header_val, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        self.set_font(_FONT, "", 8)
        self.set_fill_color(255, 255, 255)
        for row in rows:
            char_text = row[char_key].replace("\\n", "\n")
            val_text = row[val_key].replace("\\n", "\n")

            char_lines = char_text.count("\n") + 1
            val_lines = val_text.count("\n") + 1
            line_count = max(char_lines, val_lines)
            for line in char_text.split("\n"):
                line_count = max(line_count, char_lines + max(0, len(line) // 55))
            for line in val_text.split("\n"):
                line_count = max(line_count, val_lines + max(0, len(line) // 42))

            row_h = max(5 * line_count, 5)
            x_start = self.get_x()
            y_start = self.get_y()

            if y_start + row_h > self.h - 25:
                self.add_page()
                y_start = self.get_y()

            self.rect(x_start, y_start, col_w[0], row_h)
            self.rect(x_start + col_w[0], y_start, col_w[1], row_h)

            self.set_xy(x_start + 1, y_start + 1)
            self.multi_cell(col_w[0] - 2, 4, char_text)
            self.set_xy(x_start + col_w[0] + 1, y_start + 1)
            self.multi_cell(col_w[1] - 2, 4, val_text)
            self.set_xy(x_start, y_start + row_h)


# --- Section label templates (only structural, no content) ---
SECTION_LABELS = {
    "en": {
        "title": "Declaration of performance",
        "subtitle": "(as per EU Construction products regulation no. 305/2011)",
        "s1": "Unique identification code of the product-type as reference number of the declaration of performance",
        "s2": "Intended use or uses of the construction product, in accordance with the applicable harmonised technical specification, as foreseen by the manufacturer",
        "s3": "Name, registered trade name or registered trade mark and contact address of the manufacturer as required pursuant to Article 11(5)",
        "s4": "Where applicable, name and contact address of the authorised representative whose mandate covers the tasks specified in Article 12(2)",
        "s5": "System or systems of assessment and verification of constancy of performance of the construction product as set out in Annex V",
        "s6": "In case of the declaration of performance concerning a construction product for which a European Technical Assessment has been issued",
        "s7": "Declared performance",
        "eta_tab": "name and identification number of the Technical Assessment Body",
        "eta_ead": "harmonised technical specification",
        "eta_eta": "European Technical Assessment / approval",
        "eta_body": "body, system for the assessment/verification of the constancy of performance",
        "eta_cert": "certificate of conformity of the factory production",
        "place_label": "Place and date of issue",
        "perf_char": "Essential characteristics",
        "perf_val": "Performance",
    },
    "de": {
        "title": "Leistungserkl\u00e4rung",
        "subtitle": "(gem\u00e4ss EU Bauproduktenverordnung Nr. 305/2011)",
        "s1": "Eindeutiger Kenncode des Produkttyps als Bezugsnummer der Leistungserkl\u00e4rung",
        "s2": "Vom Hersteller vorgesehener Verwendungszweck oder vorgesehene Verwendungszwecke des Bauprodukts gem\u00e4ss der anwendbaren harmonisierten technischen Spezifikation",
        "s3": "Name, eingetragener Handelsname oder eingetragene Marke und Kontaktanschrift des Herstellers gem\u00e4ss Artikel 11 (5)",
        "s4": "Gegebenenfalls Name und Kontaktanschrift des Bevollm\u00e4chtigten, der mit den Aufgaben gem\u00e4ss Artikel 12 (2) beauftragt ist",
        "s5": "System oder Systeme zur Bewertung und \u00dcberpr\u00fcfung der Leistungsbest\u00e4ndigkeit des Bauprodukts gem\u00e4ss Anhang V",
        "s6": "Im Falle der Leistungserkl\u00e4rung, die ein Bauprodukt betrifft, f\u00fcr das eine Europ\u00e4ische Technische Bewertung (ETA) ausgestellt worden ist",
        "s7": "Erkl\u00e4rte Leistung",
        "eta_tab": "Name und Kennnummer der technischen Bewertungsstelle",
        "eta_ead": "Harmonisierte technische Spezifikation",
        "eta_eta": "Europ\u00e4ische technische Bewertung / Zulassung",
        "eta_body": "Stelle, System der Bewertung/\u00dcberpr\u00fcfung der Leistungsbest\u00e4ndigkeit",
        "eta_cert": "Konformit\u00e4tsbescheinigung f\u00fcr die werkseigene Produktionskontrolle",
        "place_label": "Ort und Datum der Ausstellung",
        "perf_char": "Wesentliche Merkmale",
        "perf_val": "Leistung",
    },
}


def build_dop_pdf(dop_data: dict) -> bytes:
    """Generate a DoP PDF entirely from the LLM-produced structured data."""
    code = dop_data["product_code"]
    pdf = DoPPDF(code)
    pdf.set_title(f"Declaration of Performance - {code}")

    # --- Table of Contents ---
    pdf.add_page()
    pdf.set_font(_FONT, "B", 18)
    pdf.cell(0, 12, "Declaration of Performance", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(_FONT, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, code, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(_FONT, "", 11)
    for lang in ("en", "de"):
        pdf.cell(0, 8, f"{lang.upper()} - {SECTION_LABELS[lang]['title']}", new_x="LMARGIN", new_y="NEXT")

    # --- EN + DE pages ---
    for lang in ("en", "de"):
        pdf.add_page()
        _render_dop_page(pdf, dop_data, lang)

    return pdf.output()


def _render_dop_page(pdf: DoPPDF, data: dict, lang: str):
    labels = SECTION_LABELS[lang]
    char_key = f"characteristic_{lang}"
    val_key = f"value_{lang}"

    # Title
    pdf.set_font(_FONT, "B", 14)
    pdf.cell(0, 8, labels["title"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(_FONT, "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, labels["subtitle"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Section 1 - product code (from LLM)
    pdf.section_heading("1", labels["s1"])
    pdf.section_value(data["product_code"])

    # Section 2 - intended use (from LLM)
    pdf.section_heading("2", labels["s2"])
    pdf.section_value(data.get(f"intended_use_{lang}", ""))

    # Section 3 - manufacturer (from LLM, extracted from ETA)
    pdf.section_heading("3", labels["s3"])
    pdf.section_value(data.get("manufacturer", ""))

    # Section 4 - authorised representative (from LLM)
    pdf.section_heading("4", labels["s4"])
    pdf.section_value(data.get(f"authorised_representative_{lang}", ""))

    # Section 5 - AVCP system (from LLM, extracted from ETA)
    pdf.section_heading("5", labels["s5"])
    pdf.section_value(data.get("avcp_system", ""))

    # Section 6 - ETA details (from LLM, extracted from ETA)
    pdf.section_heading("6", labels["s6"])
    eta = data.get("eta_details", {})
    eta_items = [
        (labels["eta_tab"], eta.get("tab_name", "")),
        (labels["eta_ead"], eta.get("ead_ref", "")),
        (labels["eta_eta"], eta.get("eta_ref", "")),
        (labels["eta_body"], eta.get("notified_body", "")),
        (labels["eta_cert"], eta.get("certificate", "")),
    ]
    pdf.set_font(_FONT, "", 9)
    for label, value in eta_items:
        pdf.cell(5)
        pdf.cell(0, 5, f"- {label}: {value}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 7 - performance table (from LLM, derived from EAD + product sheet)
    pdf.section_heading("7", labels["s7"])
    pdf.add_performance_table(
        data.get("performance_table", []),
        char_key, val_key,
        header_char=labels["perf_char"],
        header_val=labels["perf_val"],
    )
    pdf.ln(5)

    # Conformity + responsibility (from LLM, derived from EU-CPR)
    pdf.set_font(_FONT, "I", 9)
    pdf.multi_cell(0, 4.5, data.get(f"conformity_text_{lang}", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.multi_cell(0, 4.5, data.get(f"responsibility_text_{lang}", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Signatures (from LLM, extracted from ETA)
    pdf.set_font(_FONT, "", 9)
    pdf.multi_cell(0, 5, data.get(f"signed_by_text_{lang}", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    signatories = data.get("signatories", [])
    if signatories:
        pdf.set_font(_FONT, "B", 10)
        names = [s.get("name", "") for s in signatories]
        if len(names) >= 2:
            pdf.cell(90, 5, names[0])
            pdf.cell(0, 5, names[1], new_x="LMARGIN", new_y="NEXT")
        elif names:
            pdf.cell(0, 5, names[0], new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(_FONT, "I", 9)
        title_key = f"title_{lang}"
        titles = [s.get(title_key, "") for s in signatories]
        if len(titles) >= 2:
            pdf.cell(90, 5, titles[0])
            pdf.cell(0, 5, titles[1], new_x="LMARGIN", new_y="NEXT")
        elif titles:
            pdf.cell(0, 5, titles[0], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Place and date (from LLM)
    pdf.set_font(_FONT, "", 9)
    pdf.cell(0, 5, f"{labels['place_label']}: {data.get('place_and_date', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Original language note (from LLM)
    note = data.get(f"original_language_note_{lang}", "")
    if note:
        pdf.set_font(_FONT, "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 4, note, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
