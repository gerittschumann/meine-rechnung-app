from fpdf import FPDF
import datetime

def generate_pdf(dokument, positionen, einstellungen):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------------------------------------------
    # HEADER
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, einstellungen["firmenname"], ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, einstellungen["strasse"], ln=True)
    pdf.cell(0, 6, f"{einstellungen['plz']} {einstellungen['ort']}", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # DOKUMENTDATEN
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"{dokument['typ'].capitalize()} {dokument['nummer']}", ln=True)

    pdf.set_font("Arial", "", 12)
    datum = datetime.datetime.now().strftime("%d.%m.%Y")
    pdf.cell(0, 6, f"Datum: {datum}", ln=True)
    pdf.ln(5)

    # ---------------------------------------------------
    # POSITIONEN
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, "Beschreibung")
    pdf.cell(20, 8, "Menge")
    pdf.cell(30, 8, "Preis")
    pdf.cell(30, 8, "Gesamt", ln=True)

    pdf.set_font("Arial", "", 12)

    gesamt_summe = 0

    for pos in positionen:
        pdf.cell(100, 8, pos["beschreibung"])
        pdf.cell(20, 8, str(pos["menge"]))
        pdf.cell(30, 8, f"{pos['preis']:.2f} €")
        pdf.cell(30, 8, f"{pos['gesamt']:.2f} €", ln=True)

        gesamt_summe += pos["gesamt"]

    pdf.ln(10)

    # ---------------------------------------------------
    # SUMME
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Gesamtbetrag: {gesamt_summe:.2f} €", ln=True)

    # ---------------------------------------------------
    # RÜCKGABE ALS BYTES (WICHTIG!)
    # ---------------------------------------------------
    return bytes(pdf.output(dest="S"))
