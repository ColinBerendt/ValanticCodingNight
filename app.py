import os
import tempfile
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv

load_dotenv()

from pdf_extractor import extract_text
from dop_generator import generate_dop
from pdf_builder import build_dop_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if "product_sheet" not in request.files:
        return render_template("index.html", error="No file uploaded.")

    file = request.files["product_sheet"]
    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return render_template("index.html", error="Please upload a PDF file.")

    # Save uploaded file temporarily
    upload_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(upload_path)

    try:
        product_text = extract_text(upload_path)
        if not product_text.strip():
            return render_template("index.html", error="Could not extract text from the PDF.")

        dop_data = generate_dop(product_text)
        pdf_bytes = build_dop_pdf(dop_data)

        product_code = dop_data.get("product_code", "product")
        filename = f"DoP_{product_code}.pdf"

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(pdf_bytes)
        tmp.close()

        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
    except Exception as e:
        return render_template("index.html", error=f"Generation failed: {e}")
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
