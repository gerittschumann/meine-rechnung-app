from fpdf import FPDF
import datetime
import base64
from utils.db import get_connection


# ---------------------------------------------------
# PDF GENERATOR – EINHEITLICH FÜR ALLE DOKUMENTE
# ---------------------------------------------------
def generate_pdf(daten, positionen, extra):
    """
    daten = {
        typ: rechnung / angebot / quittung
        nummer: Dokumentnummer
        kunde: Kundendaten (dict)
        rechnung: Rechnungsdaten (nur bei Quittung)
        signatur: PNG (nur bei Quittung)
        preview: True/False
    }
    """

    typ = daten.get("typ")
    nummer = daten.get("nummer")
    kunde = daten.get("kunde")
    rechnung = daten.get("rechnung")
    signatur = daten.get("signatur")
    preview = daten.get("preview", False)

    # ---------------------------------------------------
    # EINSTELLUNGEN LADEN
    # ---------------------------------------------------
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM einstellungen WHERE id = 1")
    ein = cur.fetchone()
    conn.close()

    firma = ein["firma_name"]
    adresse = ein["firma_adresse"]
    plz = ein["firma_plz"]
    ort = ein["firma_ort"]
    steuernummer = ein["steuernummer"]
    iban = ein["iban"]
    bic = ein["bic"]

    text_rechnung = ein.get("text_rechnung", "")
    text_angebot = ein.get("text_angebot", "")
    text_quittung = ein.get("text_quittung", "")

    # ---------------------------------------------------
    # PDF START
    # ---------------------------------------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------------------------------------------
    # KOPF
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, firma, ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, adresse, ln=True)
    pdf.cell(0, 6, f"{plz} {ort}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, typ.upper(), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Nummer: {nummer}", ln=True)
    pdf.cell(0, 8, f"Datum: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    pdf.ln(5)

    # ---------------------------------------------------
    # KUNDENDATEN
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Kunde:", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, kunde["name"], ln=True)
    pdf.cell(0, 6, kunde["adresse"], ln=True)
    pdf.cell(0, 6, f"{kunde['plz']} {kunde['ort']}", ln=True)
    pdf.ln(5)

    # ---------------------------------------------------
    # POSITIONEN
    # ---------------------------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Positionen:", ln=True)

    pdf.set_font("Arial", "", 12)

    for pos in positionen:
        pdf.cell(0, 6, f"- {pos['beschreibung']} ({pos['menge']} x {pos['preis']} €)", ln=True)

    pdf.ln(5)

    # ---------------------------------------------------
    # SUMME
    # ---------------------------------------------------
    summe = sum([p["gesamt"] for p in positionen])
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Gesamtsumme: {summe:.2f} €", ln=True)
    pdf.ln(10)

    # ---------------------------------------------------
    # DOKUMENTTEXT JE NACH TYP
    # ---------------------------------------------------
    pdf.set_font("Arial", "", 12)

    if typ == "rechnung":
        pdf.multi_cell(0, 6, text_rechnung)

    elif typ == "angebot":
        pdf.multi_cell(0, 6, text_angebot)

    elif typ == "quittung":
        pdf.multi_cell(0, 6, text_quittung)
        pdf.ln(10)

        # ---------------------------------------------------
        # SIGNATUR EINBINDEN
        # ---------------------------------------------------
        if signatur is not None:
            try:
                pdf.image(signatur, x=10, w=60)
            except:
                pass

    pdf.ln(10)

    # ---------------------------------------------------
    # FIRMENDATEN UNTEN
    # ---------------------------------------------------
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Steuernummer: {steuernummer}", ln=True)
    pdf.cell(0, 6, f"IBAN: {iban}", ln=True)
    pdf.cell(0, 6, f"BIC: {bic}", ln=True)

    # ---------------------------------------------------
    # PDF ALS BYTES ZURÜCKGEBEN
    # ---------------------------------------------------
    return pdf.output(dest="S").encode("latin1")
