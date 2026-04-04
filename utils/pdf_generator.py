from fpdf import FPDF

def safe(text: str) -> str:
    if not text:
        return ""
    return (
        text.replace("–", "-")
            .replace("×", "x")
            .replace("€", "EUR")
    )

def generate_pdf(eintrag, kunde, firma, positionen):
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
    pdf.cell(0, 6, safe(firma.get("firma_name", "")), ln=True)
    pdf.cell(0, 6, safe(firma.get("firma_adresse", "")), ln=True)
    pdf.cell(0, 6, safe(f"{firma.get('firma_plz', '')} {firma.get('firma_ort', '')}"), ln=True)

    if firma.get("steuernummer"):
        pdf.cell(0, 6, safe(f"Steuernummer: {firma.get('steuernummer')}"), ln=True)

    if firma.get("iban"):
        pdf.cell(0, 6, safe(f"IBAN: {firma.get('iban')}"), ln=True)

    if firma.get("bic"):
        pdf.cell(0, 6, safe(f"BIC: {firma.get('bic')}"), ln=True)

    pdf.ln(10)

    # ---------------------------------------------------
    # KUNDENDATEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, safe(kunde.get("name", "")), ln=True)
    pdf.cell(0, 6, safe(kunde.get("adresse", "")), ln=True)
    pdf.cell(0, 6, safe(f"{kunde.get('plz', '')} {kunde.get('ort', '')}"), ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # TITEL
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, safe(eintrag.get("dokument_typ", "Dokument")), ln=True)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 6, safe(f"Nummer: {eintrag.get('nummer', '')}"), ln=True)
    pdf.cell(0, 6, safe(f"Datum: {eintrag.get('datum', '')}"), ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # TEXTBLOCK
    # ---------------------------------------------------
    textblock = eintrag.get("text_rechnung", "")
    if textblock:
        pdf.multi_cell(0, 6, safe(textblock))
        pdf.ln(5)

    # ---------------------------------------------------
    # POSITIONEN
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Leistungen:", ln=True)
    pdf.set_font("Helvetica", size=12)

    gesamt = 0.0

    for pos in positionen:
        bez = safe(pos.get("bezeichnung", ""))
        menge = pos.get("menge", 1)
        preis = pos.get("preis", 0.0)
        summe = menge * preis
        gesamt += summe

        pdf.cell(0, 6, safe(f"{bez} - {menge} x {preis:.2f} EUR = {summe:.2f} EUR"), ln=True)

    pdf.ln(5)

    # ---------------------------------------------------
    # GESAMT
    # ---------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, safe(f"Gesamtbetrag: {gesamt:.2f} EUR"), ln=True)

    return pdf.output(dest="S").encode("latin1")
