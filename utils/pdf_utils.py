import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from pathlib import Path
from utils.db import load_einstellungen

# Archiv-Ordner
BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIV_DIR = BASE_DIR / "data" / "archiv"
ARCHIV_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# HILFSFUNKTION: FOOTER MIT FIRMENDATEN
# ---------------------------------------------------
def draw_footer(pdf):
    e = load_einstellungen()
    if not e:
        return

    footer_y = 40
    pdf.setFont("Helvetica", 8)

    pdf.drawString(40, footer_y + 20,
                   f"Inhaber: {e.get('inhaber_name', '')} • E-Mail: {e.get('firma_email', '')}")

    pdf.drawString(40, footer_y + 10,
                   f"{e.get('firma_name', '')} • {e.get('firma_adresse', '')} • "
                   f"{e.get('firma_plz', '')} {e.get('firma_ort', '')}")

    pdf.drawString(40, footer_y,
                   f"Steuernummer: {e.get('steuernummer', '')} • IBAN: {e.get('iban', '')} • BIC: {e.get('bic', '')}")


# ---------------------------------------------------
# RECHNUNG PDF
# ---------------------------------------------------
def create_rechnung_pdf(nummer, kunde, positionen, signatur_bytes, text_unten):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    e = load_einstellungen()

    # Kopfbereich
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 50, f"Rechnung {nummer}")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 80, f"Kunde: {kunde['name']}")
    pdf.drawString(40, height - 95, f"Adresse: {kunde['adresse']}")
    pdf.drawString(40, height - 110, f"PLZ / Ort: {kunde['plz']} {kunde['ort']}")

    # Positionen
    y = height - 150
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Beschreibung")
    pdf.drawString(350, y, "Preis (€)")
    pdf.setFont("Helvetica", 10)

    y -= 20
    gesamt = 0

    for pos in positionen:
        pdf.drawString(40, y, pos["beschreibung"])
        pdf.drawString(350, y, f"{pos['gesamt']:.2f}")
        gesamt += pos["gesamt"]
        y -= 20

    # Summe
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y - 10, f"Gesamtbetrag: {gesamt:.2f} €")

    # Standardtext
    if text_unten:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, y - 40, text_unten)

    # Signatur
    if signatur_bytes:
        try:
            pdf.drawImage(ImageReader(io.BytesIO(signatur_bytes)),
                          350, y - 120, width=120, height=60, mask="auto")
            pdf.drawString(350, y - 130, "Unterschrift")
        except Exception:
            pass

    # Footer
    draw_footer(pdf)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------
# ANGEBOT PDF
# ---------------------------------------------------
def create_angebot_pdf(nummer, kunde, positionen, text_unten):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    e = load_einstellungen()

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 50, f"Angebot {nummer}")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 80, f"Kunde: {kunde['name']}")
    pdf.drawString(40, height - 95, f"Adresse: {kunde['adresse']}")
    pdf.drawString(40, height - 110, f"PLZ / Ort: {kunde['plz']} {kunde['ort']}")

    y = height - 150
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Beschreibung")
    pdf.drawString(350, y, "Preis (€)")
    pdf.setFont("Helvetica", 10)

    y -= 20
    gesamt = 0

    for pos in positionen:
        pdf.drawString(40, y, pos["beschreibung"])
        pdf.drawString(350, y, f"{pos['gesamt']:.2f}")
        gesamt += pos["gesamt"]
        y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y - 10, f"Gesamtbetrag: {gesamt:.2f} €")

    if text_unten:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, y - 40, text_unten)

    draw_footer(pdf)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------
# QUITTUNG PDF
# ---------------------------------------------------
def create_quittung_pdf(nummer, kunde, positionen, signatur_bytes, rechnung_nummer):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    e = load_einstellungen()

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 50, f"Quittung {nummer}")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 80, f"Kunde: {kunde['name']}")
    pdf.drawString(40, height - 95, f"Rechnung zugehörig: {rechnung_nummer}")

    y = height - 140
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Beschreibung")
    pdf.drawString(350, y, "Preis (€)")
    pdf.setFont("Helvetica", 10)

    y -= 20
    gesamt = 0

    for pos in positionen:
        pdf.drawString(40, y, pos["beschreibung"])
        pdf.drawString(350, y, f"{pos['gesamt']:.2f}")
        gesamt += pos["gesamt"]
        y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y - 10, f"Gesamtbetrag: {gesamt:.2f} €")

    # Signatur
    if signatur_bytes:
        try:
            pdf.drawImage(ImageReader(io.BytesIO(signatur_bytes)),
                          350, y - 120, width=120, height=60, mask="auto")
            pdf.drawString(350, y - 130, "Unterschrift")
        except Exception:
            pass

    draw_footer(pdf)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
