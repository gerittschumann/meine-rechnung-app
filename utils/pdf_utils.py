from fpdf import FPDF

def create_document(kunde, adresse, posten, nr, typ, sign_img=None, ist_vorschau=False):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"{typ} {nr}", ln=True)
    pdf.cell(200, 10, txt=f"Kunde: {kunde}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Adresse: {adresse}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Leistung")
    pdf.cell(30, 10, "Menge")
    pdf.cell(30, 10, "Preis")
    pdf.cell(30, 10, "Gesamt", ln=True)

    pdf.set_font("Arial", size=12)
    for p in posten:
        pdf.cell(40, 10, str(p["leistung"]))
        pdf.cell(30, 10, str(p["menge"]))
        pdf.cell(30, 10, str(p["preis"]))
        pdf.cell(30, 10, str(p["gesamt"]), ln=True)

    return pdf.output(dest="S").encode("latin1")
