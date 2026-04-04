from fpdf import FPDF
from datetime import datetime

def generate_pdf(eintrag, kunde, firma, positionen):
    # Sicherheit: sqlite3.Row → dict
    eintrag = dict(eintrag)
    kunde = dict(kunde)
    firma = dict(firma)

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
    pdf.ln(5)

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
    # DOKUMENTTITEL
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, eintrag.get("dokument_typ", "Dokument"), ln=True)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, f"Nummer: {eintrag.get('nummer', '')}", ln=True)
    pdf.cell(0, 6, f"Datum: {eintrag.get('datum', '')}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # TEXTBLOCK (aus Einstellungen oder manuell)
    # ---------------------------------------------------
    textblock = eintrag.get("text_rechnung", "")

    if textblock:
        pdf.multi_cell(0, 6, textblock)
        pdf.ln(5)

    # ---------------------------------------------------
    # POSITIONEN – TABELLENFORMAT
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Leistungen / Positionen:", ln=True)
    pdf.set_font("Helvetica", size=12)

    gesamt = 0.0

    for pos in positionen:
        pos = dict(pos)
        bez = pos.get("bezeichnung", "")
        menge = pos.get("menge", 1)
        preis = pos.get("preis", 0.0)
        summe = menge * preis
        gesamt += summe

        pdf.cell(0, 6, f"{bez} – {menge} × {preis:.2f} € = {summe:.2f} €", ln=True)

    pdf.ln(5)

    # ---------------------------------------------------
    # GESAMTSUMME
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Gesamtbetrag: {gesamt:.2f} €", ln=True)

    # ---------------------------------------------------
    # QUITTUNG – SIGNATUR
    # ---------------------------------------------------
    if eintrag.get("dokument_typ", "").lower() == "quittung":
        pdf.ln(15)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Unterschrift:", ln=True)

        signatur = eintrag.get("signatur")
        if signatur is not None:
            # Signatur als PNG einfügen
            pdf.image(signatur, x=10, w=80)

    # ---------------------------------------------------
    # PDF ALS BYTES ZURÜCKGEBEN
    # ---------------------------------------------------
    return pdf.output(dest="S").encode("latin1")
