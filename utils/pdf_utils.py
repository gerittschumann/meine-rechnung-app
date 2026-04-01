from fpdf import FPDF
from utils.supabase_utils import supabase

def load_settings():
    data = supabase.table("settings").select("*").execute().data
    if len(data) == 0:
        return {
            "firma": "",
            "adresse": "",
            "km_pauschale": 0.30,
            "stundensatz": 0.0
        }
    return data[0]

class PDF(FPDF):
    def header(self):
        settings = load_settings()

        # Logo optional
        try:
            self.image("logo.png", 10, 8, 30)
        except:
            pass

        # Firmenblock
        self.set_xy(140, 10)
        self.set_font("Arial", "B", 12)
        self.multi_cell(60, 6, settings.get("firma", ""))

        self.set_font("Arial", "", 10)
        self.set_xy(140, 18)
        self.multi_cell(60, 5, settings.get("adresse", ""))

        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Erstellt am: {self.date}", 0, 0, "C")

def create_document(kunde, adresse, posten, nr, typ, sign_img=None, ist_vorschau=False):
    pdf = PDF()
    pdf.date = FPDF().date
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Titel
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{typ} {nr}", ln=True)

    # Kundendaten
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.multi_cell(0, 6, f"Kunde:\n{kunde}\n\nAdresse:\n{adresse}")
    pdf.ln(5)

    # Tabelle
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 10, "Leistung", 1, 0, "L", True)
    pdf.cell(30, 10, "Menge", 1, 0, "C", True)
    pdf.cell(40, 10, "Preis (€)", 1, 0, "C", True)
    pdf.cell(40, 10, "Gesamt (€)", 1, 1, "C", True)

    pdf.set_font("Arial", "", 12)

    summe = 0

    for p in posten:
        pdf.cell(80, 10, str(p["leistung"]), 1)
        pdf.cell(30, 10, str(p["menge"]), 1, 0, "C")
        pdf.cell(40, 10, f"{p['preis']:.2f}", 1, 0, "C")
        pdf.cell(40, 10, f"{p['gesamt']:.2f}", 1, 1, "C")
        summe += p["gesamt"]

    # Summe
    pdf.set_font("Arial", "B", 12)
    pdf.cell(150, 10, "Summe", 1)
    pdf.cell(40, 10, f"{summe:.2f} €", 1, 1, "C")

    # Signatur optional
    if sign_img:
        pdf.ln(10)
        pdf.image(sign_img, x=10, w=60)

    return pdf.output(dest="S").encode("latin1")
