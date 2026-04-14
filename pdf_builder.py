import os
from fpdf import FPDF

FONT_DIR = os.path.join(os.path.dirname(__file__), "static")
_FONT = "DejaVu"

# SFS brand + neutrals
SFS_RED = (235, 60, 36)
SFS_RED_DARK = (180, 42, 28)
SFS_RED_LIGHT = (254, 242, 240)
INK = (26, 26, 26)
INK_MUTED = (90, 90, 90)
PAPER = (252, 252, 252)
RULE = (220, 220, 220)


class DoPPDF(FPDF):
    def __init__(self, product_code: str):
        super().__init__()
        self.product_code = product_code
        self.set_auto_page_break(auto=True, margin=28)
        self.add_font(_FONT, "", os.path.join(FONT_DIR, "DejaVuSans.ttf"), uni=True)
        self.add_font(_FONT, "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), uni=True)
        self.add_font(_FONT, "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"), uni=True)

    def header(self):
        # Title + TOC pages have their own layout
        if self.page_no() <= 2:
            return
        self.set_draw_color(*SFS_RED)
        self.set_line_width(0.8)
        self.line(self.l_margin, 12, self.w - self.r_margin, 12)
        self.set_y(14)
        self.set_font(_FONT, "B", 9)
        self.set_text_color(*SFS_RED)
        self.cell(0, 5, f"DoP  {self.product_code}", align="L")
        self.set_font(_FONT, "I", 8)
        self.set_text_color(*INK_MUTED)
        self.cell(0, 5, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(4)

    def footer(self):
        if self.page_no() <= 2:
            return
        self.set_y(-16)
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(1)
        self.set_font(_FONT, "I", 7)
        self.set_text_color(*INK_MUTED)
        self.cell(0, 4, "EU-CPR 305/2011  |  Declaration of Performance", align="C")

    def section_heading(self, number: str, text: str):
        y0 = self.get_y()
        self.set_fill_color(*SFS_RED)
        self.rect(self.l_margin, y0, 4, 6, "F")
        self.set_xy(self.l_margin + 7, y0)
        self.set_font(_FONT, "B", 9.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, f"{number}.  {text}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def section_value(self, text: str):
        self.set_font(_FONT, "", 9.5)
        self.set_text_color(45, 45, 45)
        x = self.l_margin + 2
        self.set_x(x)
        self.set_fill_color(*SFS_RED_LIGHT)
        w = self.w - self.r_margin - self.l_margin - 2
        self.multi_cell(w, 5, text, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(*INK)
        self.ln(4)

    def add_performance_table(self, rows: list[dict], char_key: str, val_key: str,
                              header_char: str, header_val: str):
        col_w = [102, 78]
        self.set_font(_FONT, "B", 8.5)
        self.set_fill_color(*SFS_RED)
        self.set_text_color(255, 255, 255)
        self.cell(col_w[0], 8, f"  {header_char}", border="LTRB", fill=True)
        self.cell(col_w[1], 8, f"  {header_val}", border="LTRB", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)

        self.set_font(_FONT, "", 8)
        alt = False
        for row in rows:
            char_text = row[char_key].replace("\\n", "\n")
            val_text = row[val_key].replace("\\n", "\n")

            char_lines = char_text.count("\n") + 1
            val_lines = val_text.count("\n") + 1
            line_count = max(char_lines, val_lines)
            for line in char_text.split("\n"):
                line_count = max(line_count, char_lines + max(0, len(line) // 52))
            for line in val_text.split("\n"):
                line_count = max(line_count, val_lines + max(0, len(line) // 38))

            row_h = max(5 * line_count, 5)
            x_start = self.get_x()
            y_start = self.get_y()

            if y_start + row_h > self.h - 28:
                self.add_page()
                y_start = self.get_y()

            if alt:
                self.set_fill_color(255, 252, 251)
            else:
                self.set_fill_color(255, 255, 255)
            alt = not alt
            self.rect(x_start, y_start, col_w[0] + col_w[1], row_h, "F")
            self.set_draw_color(*RULE)
            self.rect(x_start, y_start, col_w[0], row_h)
            self.rect(x_start + col_w[0], y_start, col_w[1], row_h)

            self.set_xy(x_start + 1.5, y_start + 1)
            self.multi_cell(col_w[0] - 2, 4, char_text)
            self.set_xy(x_start + col_w[0] + 1.5, y_start + 1)
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


def _render_title_page(pdf: DoPPDF, code: str, place_and_date: str) -> None:
    """Bold cover: red geometry, oversized type, CE-energy vibe."""
    w, h = pdf.w, pdf.h
    lm = pdf.l_margin

    # Base
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, w, h, "F")

    # Giant diagonal red slab (polygon via filled triangles / quads approximated with rects)
    pdf.set_fill_color(*SFS_RED_DARK)
    for i in range(0, 115, 3):
        pdf.set_fill_color(
            int(SFS_RED_DARK[0] + (SFS_RED[0] - SFS_RED_DARK[0]) * (i / 115)),
            int(SFS_RED_DARK[1] + (SFS_RED[1] - SFS_RED_DARK[1]) * (i / 115)),
            int(SFS_RED_DARK[2] + (SFS_RED[2] - SFS_RED_DARK[2]) * (i / 115)),
        )
        pdf.rect(0, i * 0.85, w, 4, "F")

    pdf.set_fill_color(*SFS_RED)
    pdf.rect(0, 0, w, 52, "F")

    # Accent stripes (right side)
    pdf.set_fill_color(255, 255, 255)
    for i, xoff in enumerate((168, 176, 184)):
        alpha_h = 28 - i * 6
        pdf.rect(xoff, 8 + i * 5, 3, max(alpha_h, 8), "F")

    # Oversized watermark letters
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(_FONT, "B", 82)
    pdf.set_xy(lm, 18)
    pdf.cell(0, 28, "CE", align="L")
    pdf.set_font(_FONT, "B", 22)
    pdf.set_xy(lm + 52, 36)
    pdf.cell(0, 10, "DoP", align="L")

    # Main headline stack
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(_FONT, "B", 11)
    pdf.set_xy(lm, 58)
    pdf.cell(0, 5, "CONSTRUCTION PRODUCTS REGULATION", align="L")
    pdf.set_font(_FONT, "B", 17)
    pdf.set_xy(lm, 66)
    pdf.multi_cell(0, 7, "DECLARATION\nOF PERFORMANCE", new_x="LMARGIN", new_y="NEXT")

    # Product code — huge
    pdf.set_font(_FONT, "B", 36)
    pdf.set_text_color(*INK)
    pdf.set_xy(lm, 98)
    pdf.cell(0, 16, code, align="L")

    pdf.set_draw_color(*SFS_RED)
    pdf.set_line_width(1.2)
    pdf.line(lm, 118, lm + min(140, pdf.get_string_width(code) + 8), 118)

    # Tagline block
    pdf.set_font(_FONT, "I", 10)
    pdf.set_text_color(*INK_MUTED)
    pdf.set_xy(lm, 124)
    pdf.multi_cell(
        w - lm - pdf.r_margin,
        5,
        "Mechanical fasteners  |  EAD 030351-00-0402  |  ETA-23/0859",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Crazy ticker-style banner
    pdf.set_fill_color(*SFS_RED)
    pdf.rect(0, 148, w, 10, "F")
    pdf.set_font(_FONT, "B", 7)
    pdf.set_text_color(255, 255, 255)
    ticker = (
        "  PERFORMANCE  *  SAFETY  *  TRACEABILITY  *  EU MARKET  *  AVCP 2+  *  "
        "PERFORMANCE  *  SAFETY  *  TRACEABILITY  *  "
    )
    pdf.set_xy(0, 149.5)
    pdf.cell(w, 7, ticker, align="C")

    # White card: meta
    card_y = 168
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.4)
    pdf.rect(lm - 2, card_y, w - lm - pdf.r_margin + 4, 38, style="FD")

    pdf.set_xy(lm + 4, card_y + 5)
    pdf.set_font(_FONT, "B", 10)
    pdf.set_text_color(*SFS_RED)
    pdf.cell(0, 6, "Document snapshot", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(lm + 4)
    pdf.set_font(_FONT, "", 9)
    pdf.set_text_color(*INK)
    pdf.multi_cell(
        w - lm - pdf.r_margin - 8,
        5,
        f"Product-type reference:  {code}\n"
        f"Issue (if stated):  {place_and_date or '—'}\n"
        "Languages inside:  English  +  German",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Bottom mega strip + dots
    pdf.set_fill_color(*SFS_RED_DARK)
    pdf.rect(0, h - 22, w, 22, "F")
    pdf.set_font(_FONT, "B", 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(lm, h - 18)
    pdf.cell(0, 5, "SFS Group  |  Division Construction  |  CE marking workflow", align="L")
    pdf.set_font(_FONT, "I", 8)
    pdf.set_xy(lm, h - 12)
    pdf.cell(0, 4, "Turn the page for contents and full DoP text.", align="L")

    # Decorative circles
    pdf.set_fill_color(255, 100, 80)
    for cx, cy, r in ((175, 125, 4), (185, 138, 3), (165, 135, 2.5)):
        pdf.ellipse(cx - r, cy - r, 2 * r, 2 * r, "F")


def _render_toc_page(pdf: DoPPDF, code: str) -> None:
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, pdf.w, pdf.h, "F")

    pdf.set_font(_FONT, "B", 20)
    pdf.set_text_color(*SFS_RED)
    pdf.cell(0, 14, "Contents", align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.set_draw_color(*SFS_RED)
    pdf.set_line_width(0.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(8)

    entries = [
        ("1", "Cover", "Visual front page"),
        ("2", "Contents", "This overview"),
        ("3", "EN", SECTION_LABELS["en"]["title"]),
        ("4", "DE", SECTION_LABELS["de"]["title"]),
    ]
    for num, tag, title in entries:
        pdf.set_font(_FONT, "B", 11)
        pdf.set_text_color(*SFS_RED)
        pdf.cell(12, 8, num, align="L")
        pdf.set_font(_FONT, "B", 11)
        pdf.set_text_color(*INK)
        pdf.cell(22, 8, tag, align="L")
        pdf.set_font(_FONT, "", 10)
        pdf.set_text_color(*INK_MUTED)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    pdf.ln(10)
    y_card = pdf.get_y()
    pdf.set_fill_color(*SFS_RED_LIGHT)
    pdf.set_draw_color(*RULE)
    pdf.rect(pdf.l_margin, y_card, pdf.w - pdf.l_margin - pdf.r_margin, 22, style="FD")
    pdf.set_xy(pdf.l_margin + 4, y_card + 4)
    pdf.set_font(_FONT, "B", 9)
    pdf.set_text_color(*INK)
    pdf.cell(0, 5, f"Product-type:  {code}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 4)
    pdf.set_font(_FONT, "", 8)
    pdf.set_text_color(*INK_MUTED)
    pdf.multi_cell(
        pdf.w - pdf.l_margin - pdf.r_margin - 8,
        4,
        "Sections 1 to 7 on the following pages follow the mandatory CPR structure.",
    )
    pdf.set_y(y_card + 22)


def build_dop_pdf(dop_data: dict) -> bytes:
    """Generate a DoP PDF entirely from the LLM-produced structured data."""
    code = dop_data["product_code"]
    place = dop_data.get("place_and_date", "")
    pdf = DoPPDF(code)
    pdf.set_title(f"Declaration of Performance - {code}")

    pdf.add_page()
    _render_title_page(pdf, code, place)

    pdf.add_page()
    _render_toc_page(pdf, code)

    for lang in ("en", "de"):
        pdf.add_page()
        _render_dop_page(pdf, dop_data, lang)

    return pdf.output()


def _render_dop_page(pdf: DoPPDF, data: dict, lang: str):
    labels = SECTION_LABELS[lang]
    char_key = f"characteristic_{lang}"
    val_key = f"value_{lang}"

    # Title band
    pdf.set_fill_color(*SFS_RED_LIGHT)
    pdf.set_draw_color(*SFS_RED)
    pdf.set_line_width(0.5)
    band_h = 22
    pdf.rect(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin - pdf.r_margin, band_h, style="FD")
    y_in = pdf.get_y()
    pdf.set_xy(pdf.l_margin + 4, y_in + 4)
    pdf.set_font(_FONT, "B", 13)
    pdf.set_text_color(*SFS_RED)
    pdf.cell(0, 7, labels["title"].upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 4)
    pdf.set_font(_FONT, "I", 8.5)
    pdf.set_text_color(*INK_MUTED)
    pdf.cell(0, 5, labels["subtitle"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK)
    pdf.set_y(y_in + band_h + 4)

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
        pdf.set_x(pdf.l_margin + 2)
        pdf.set_fill_color(248, 248, 248)
        pdf.multi_cell(
            pdf.w - pdf.l_margin - pdf.r_margin - 2,
            5,
            f"  {label}:  {value}",
            new_x="LMARGIN",
            new_y="NEXT",
            fill=True,
        )
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
    y_legal = pdf.get_y()
    pdf.set_font(_FONT, "I", 8.5)
    pdf.set_text_color(55, 55, 55)
    c_text = data.get(f"conformity_text_{lang}", "")
    r_text = data.get(f"responsibility_text_{lang}", "")
    inner_w = pdf.w - pdf.l_margin - pdf.r_margin - 6
    lh = 4.3
    combined = f"{c_text}\n{r_text}".strip()
    chars_per_line = max(24, int(inner_w / 2.05))
    n_lines = 0
    for para in combined.split("\n"):
        plen = len(para) if para else 1
        n_lines += max(1, (plen + chars_per_line - 1) // chars_per_line)
    box_h = max(24, n_lines * lh + 10)

    pdf.set_fill_color(*SFS_RED_LIGHT)
    pdf.set_draw_color(*RULE)
    pdf.rect(pdf.l_margin, y_legal, pdf.w - pdf.l_margin - pdf.r_margin, box_h, style="FD")
    pdf.set_xy(pdf.l_margin + 3, y_legal + 3)
    pdf.multi_cell(inner_w, lh, c_text)
    pdf.set_x(pdf.l_margin + 3)
    pdf.multi_cell(inner_w, lh, r_text)
    pdf.set_y(y_legal + box_h + 4)

    # Signatures (from LLM, extracted from ETA)
    pdf.set_font(_FONT, "B", 9)
    pdf.set_text_color(*SFS_RED)
    pdf.multi_cell(0, 5, data.get(f"signed_by_text_{lang}", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK)
    pdf.ln(2)

    signatories = data.get("signatories", [])
    if signatories:
        pdf.set_font(_FONT, "B", 10)
        names = [s.get("name", "") for s in signatories]
        if len(names) >= 2:
            pdf.cell(92, 5, names[0])
            pdf.cell(0, 5, names[1], new_x="LMARGIN", new_y="NEXT")
        elif names:
            pdf.cell(0, 5, names[0], new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(_FONT, "I", 9)
        title_key = f"title_{lang}"
        titles = [s.get(title_key, "") for s in signatories]
        if len(titles) >= 2:
            pdf.cell(92, 5, titles[0])
            pdf.cell(0, 5, titles[1], new_x="LMARGIN", new_y="NEXT")
        elif titles:
            pdf.cell(0, 5, titles[0], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Place and date (from LLM)
    pdf.set_font(_FONT, "B", 9)
    pdf.set_text_color(*SFS_RED)
    pdf.cell(0, 5, f"{labels['place_label']}: {data.get('place_and_date', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK)
    pdf.ln(2)

    # Original language note (from LLM)
    note = data.get(f"original_language_note_{lang}", "")
    if note:
        pdf.set_font(_FONT, "I", 8)
        pdf.set_text_color(*INK_MUTED)
        pdf.multi_cell(0, 4, note, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*INK)
