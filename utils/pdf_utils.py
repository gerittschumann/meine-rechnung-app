from fpdf import FPDF
from io import BytesIO
import base64
from pathlib import Path

ARCHIV_DIR = Path("data/archiv")
ARCHIV_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# PDF ERZEUGEN (Alternative zu pdf_generator.py)
# ---------------------------------------------------
def create_pdf(kunde, positionen, summe, dokument_typ, dokument_nr, firma=None, textblock=""):
    """
    Erzeugt ein PDF-Dokument (FPDF) und gibt es als Bytes zurück.
    Wird für Vorschau oder Archivierung genutzt.
    """

    kunde = dict(kunde)
    firma = dict(firma) if firma else {}

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------------------------------------------
    # FIRMENDATEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, firma.get("firma_name", ""), ln=True)
    pdf.cell(0, 6, firma.get("firma_adresse", ""), ln=True)
    pdf.cell(0, 6, f"{firma.get('firma_plz', '')} {firma.get('firma_ort', '')}", ln=True)

    if firma.get("steuernummer"):
        pdf.cell(0, 6, f"Steuernummer: {firma.get('steuernummer')}", ln=True)

    if firma.get("iban"):
        pdf.cell(0, 6, f"IBAN: {firma.get('iban')}", ln=True)

    if firma.get("bic"):
        pdf.cell(0, 6, f"BIC: {firma.get('bic')}", ln=True)

    pdf.ln(10)

    # ---------------------------------------------------
    # KUNDENDATEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, kunde.get("name", ""), ln=True)
    pdf.cell(0, 6, kunde.get("adresse", ""), ln=True)
    pdf.cell(0, 6, f"{kunde.get('plz', '')} {kunde.get('ort', '')}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # TITEL
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"{dokument_typ} {dokument_nr}", ln=True)
    pdf.ln(5)

    # ---------------------------------------------------
    # TEXTBLOCK
    # ---------------------------------------------------
    if textblock:
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 6, textblock)
        pdf.ln(5)

    # ---------------------------------------------------
    # POSITIONEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Leistungen:", ln=True)
    pdf.set_font("Helvetica", size=12)

    for pos in positionen:
        pos = dict(pos)
        bez = pos.get("bezeichnung", "")
        menge = pos.get("menge", 1)
        preis = pos.get("preis", 0.0)
        gesamt = menge * preis

        pdf.cell(0, 6, f"{bez} – {menge} × {preis:.2f} € = {gesamt:.2f} €", ln=True)

    pdf.ln(5)

    # ---------------------------------------------------
    # SUMME
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Gesamtbetrag: {summe:.2f} €", ln=True)

    # ---------------------------------------------------
    # PDF ALS BYTES
    # ---------------------------------------------------
    return pdf.output(dest="S").encode("latin1")


# ---------------------------------------------------
# PDF ALS DATA-URL (für Browser-Vorschau)
# ---------------------------------------------------
def pdf_bytes_to_data_url(pdf_bytes: bytes) -> str:
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return f"data:application/pdf;base64,{b64}"


# ---------------------------------------------------
# PDF IM ARCHIV SPEICHERN
# ---------------------------------------------------
def save_pdf_to_archiv(pdf_bytes: bytes, nummer: str) -> Path:
    """
    Speichert ein PDF im Archiv (/mnt/data/archiv).
    """
    ARCHIV_DIR.mkdir(parents=True, exist_ok=True)
    path = ARCHIV_DIR / f"{nummer}.pdf"

    with open(path, "wb") as f:
        f.write(pdf_bytes)

    return path
