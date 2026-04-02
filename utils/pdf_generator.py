from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from io import BytesIO
import datetime

def generate_pdf(dokument, positionen, einstellungen):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Schriftart
    c.setFont("Helvetica", 12)

    # ---------------------------------------------------
    # EINSTELLUNGEN (SQLite-kompatibel)
    # ---------------------------------------------------
    firma = einstellungen.get("firma_name", "")
    adresse = einstellungen.get("firma_adresse", "")
    plz = einstellungen.get("firma_plz", "")
    ort = einstellungen.get("firma_ort", "")

    y = 800

    # ---------------------------------------------------
    # HEADER
    # ---------------------------------------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, y, firma)
    y -= 10*mm

    c.setFont("Helvetica", 12)
    c.drawString(20*mm, y, adresse)
    y -= 6*mm
    c.drawString(20*mm, y, f"{plz} {ort}")
    y -= 15*mm

    # ---------------------------------------------------
    # DOKUMENTDATEN
    # ---------------------------------------------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, f"{dokument['typ'].capitalize()} {dokument['nummer']}")
    y -= 10*mm

    c.setFont("Helvetica", 12)
    datum = datetime.datetime.now().strftime("%d.%m.%Y")
    c.drawString(20*mm, y, f"Datum: {datum}")
    y -= 15*mm

    # ---------------------------------------------------
    # POSITIONEN
    # ---------------------------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, "Beschreibung")
    c.drawString(110*mm, y, "Menge")
    c.drawString(130*mm, y, "Preis")
    c.drawString(160*mm, y, "Gesamt")
    y -= 8*mm

    c.setFont("Helvetica", 12)

    gesamt_summe = 0

    for pos in positionen:
        c.drawString(20*mm, y, pos["beschreibung"])
        c.drawString(110*mm, y, str(pos["menge"]))
        c.drawString(130*mm, y, f"{pos['preis']:.2f} €")
        c.drawString(160*mm, y, f"{pos['gesamt']:.2f} €")
        y -= 8*mm

        gesamt_summe += pos["gesamt"]

    y -= 10*mm

    # ---------------------------------------------------
    # SUMME
    # ---------------------------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, f"Gesamtbetrag: {gesamt_summe:.2f} €")

    # ---------------------------------------------------
    # PDF ABSCHLIESSEN
    # ---------------------------------------------------
    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
