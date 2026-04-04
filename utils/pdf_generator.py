from fpdf import FPDF
from datetime import datetime

def generate_pdf(ein, kunden_daten, firma_daten, leistungen):
    # sqlite3.Row → dict konvertieren, damit .get() funktioniert
    ein = dict(ein)
    kunden_daten = dict(kunden_daten)
    firma_daten = dict(firma_daten)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------------------------------------------
    # FIRMENDATEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, firma_daten.get("firmenname", ""), ln=True)
    pdf.cell(0, 6, firma_daten.get("strasse", ""), ln=True)
    pdf.cell(0, 6, f"{firma_daten.get('plz', '')} {firma_daten.get('ort', '')}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # KUNDENDATEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, kunden_daten.get("name", ""), ln=True)
    pdf.cell(0, 6, kunden_daten.get("strasse", ""), ln=True)
    pdf.cell(0, 6, f"{kunden_daten.get('plz', '')} {kunden_daten.get('ort', '')}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # RECHNUNGS-/ANGEBOTSINFOS
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, ein.get("dokument_typ", "Dokument"), ln=True)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, f"Nummer: {ein.get('nummer', '')}", ln=True)
    pdf.cell(0, 6, f"Datum: {ein.get('datum', '')}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # TEXTBLOCK
    # ---------------------------------------------------
    text_rechnung = ein.get("text_rechnung", "")
    if text_rechnung:
        pdf.multi_cell(0, 6, text_rechnung)
        pdf.ln(5)

    # ---------------------------------------------------
    # LEISTUNGEN / POSITIONEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Leistungen:", ln=True)
    pdf.set_font("Helvetica", size=12)

    gesamt = 0.0

    for pos in leistungen:
        pos = dict(pos)  # Sicherheit
        bezeichnung = pos.get("bezeichnung", "")
        menge = pos.get("menge", 1)
        preis = pos.get("preis", 0.0)
        summe = menge * preis
        gesamt += summe

        pdf.cell(0, 6, f"{bezeichnung} – {menge} × {preis:.2f} € = {summe:.2f} €", ln=True)

    pdf.ln(5)

    # ---------------------------------------------------
    # GESAMTSUMME
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Gesamt: {gesamt:.2f} €", ln=True)

    # ---------------------------------------------------
    # PDF ALS BYTES ZURÜCKGEBEN
    # ---------------------------------------------------
    return pdf.output(dest="S").encode("latin1")
