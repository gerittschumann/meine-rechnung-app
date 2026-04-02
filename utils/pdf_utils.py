from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def create_pdf(kunde, positionen, summe, dokument_typ, dokument_nr):
    """
    Erzeugt ein PDF-Dokument und gibt es als Bytes zurück.
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Kopfbereich
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, 800, f"{dokument_typ} #{dokument_nr}")

    # Kundendaten
    c.setFont("Helvetica", 12)
    c.drawString(40, 770, f"Kunde: {kunde['name']}")
    c.drawString(40, 755, f"Adresse: {kunde.get('adresse', '-')}")
    c.drawString(40, 740, f"E-Mail: {kunde.get('email', '-')}")
    c.drawString(40, 725, f"Telefon: {kunde.get('telefon', '-')}")

    # Positionen
    y = 690
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Positionen:")
    y -= 20

    c.setFont("Helvetica", 11)
    for pos in positionen:
        c.drawString(40, y, f"{pos['bezeichnung']} (x{pos['menge']})")
        c.drawRightString(550, y, f"{pos['gesamtpreis']:.2f} €")
        y -= 20

    # Summe
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y - 20, f"Gesamtsumme: {summe:.2f} €")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
