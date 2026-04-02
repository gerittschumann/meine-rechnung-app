from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Logo
        if self.logo_url:
            try:
                self.image(self.logo_url, 10, 8, 30)
                self.set_y(25)
            except:
                self.set_y(15)

        # Firmenname
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.firmenname, ln=True, align="R")

        # Kontaktinfos
        self.set_font("Helvetica", "", 10)
        kontakt = f"{self.adresse}\n{self.telefon}\n{self.email}\n{self.website}"
        self.multi_cell(0, 5, kontakt, align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", "", 9)

        footer_text = (
            f"Kontoinhaber: {self.kontoinhaber}\n"
            f"IBAN: {self.iban}   BIC: {self.bic}"
        )

        self.multi_cell(0, 5, footer_text, align="C")

def generate_pdf(dokument, positionen, einstellungen):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Einstellungen in PDF speichern
    pdf.firmenname = einstellungen.get("firmenname", "")
    pdf.adresse = einstellungen.get("adresse", "")
    pdf.telefon = einstellungen.get("telefon", "")
    pdf.email = einstellungen.get("email", "")
    pdf.website = einstellungen.get("website", "")
    pdf.steuernummer = einstellungen.get("steuernummer", "")
    pdf.logo_url = einstellungen.get("logo_url", "")

    pdf.kontoinhaber = einstellungen.get("kontoinhaber", "")
    pdf.iban = einstellungen.get("iban", "")
    pdf.bic = einstellungen.get("bic", "")

    pdf.kleinunternehmer_hinweis = einstellungen.get("kleinunternehmer_hinweis", "")
    pdf.text_rechnung = einstellungen.get("text_rechnung", "")
    pdf.text_angebot = einstellungen.get("text_angebot", "")
    pdf.text_quittung = einstellungen.get("text_quittung", "")

    pdf.add_page()

    # Dokumentkopf
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, dokument["typ"].upper(), ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Nummer: {dokument['nummer']}", ln=True)
    pdf.cell(0, 8, f"Datum: {dokument['erstellt_am'][:10]}", ln=True)
    pdf.cell(0, 8, f"Steuernummer: {pdf.steuernummer}", ln=True)
    pdf.ln(5)

    # Positionen-Tabelle
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(100, 8, "Beschreibung")
    pdf.cell(30, 8, "Menge", align="R")
    pdf.cell(30, 8, "Preis", align="R")
    pdf.cell(30, 8, "Gesamt", align="R", ln=True)

    pdf.set_font("Helvetica", "", 11)
    summe = 0

    for pos in positionen:
        pdf.cell(100, 8, pos["beschreibung"])
        pdf.cell(30, 8, str(pos["menge"]), align="R")
        pdf.cell(30, 8, f"{pos['preis']:.2f} €", align="R")
        pdf.cell(30, 8, f"{pos['gesamt']:.2f} €", align="R", ln=True)
        summe += pos["gesamt"]

    pdf.ln(5)

    # Gesamtsumme
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Gesamtsumme: {summe:.2f} €", ln=True)

    # Kleinunternehmer-Hinweis
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, pdf.kleinunternehmer_hinweis)
    pdf.ln(5)

    # Individueller Text
    pdf.set_font("Helvetica", "", 11)

    if dokument["typ"] == "rechnung":
        pdf.multi_cell(0, 6, pdf.text_rechnung)
    elif dokument["typ"] == "angebot":
        pdf.multi_cell(0, 6, pdf.text_angebot)
    elif dokument["typ"] == "quittung":
        pdf.multi_cell(0, 6, pdf.text_quittung)

    # PDF zurückgeben
    return pdf.output(dest="S").encode("latin-1")
