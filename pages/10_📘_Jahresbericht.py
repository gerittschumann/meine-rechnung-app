import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase, upload_pdf_to_supabase
from utils.pdf_utils import PDF, load_settings

st.title("📘 Jahresbericht – PDF erstellen")

# -----------------------------
# DATEN LADEN
# -----------------------------
def load_belege():
    data = supabase.table("belege").select("*").execute().data
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["datum", "typ", "betrag"])
    df["datum"] = pd.to_datetime(df["datum"], errors="coerce")
    return df

def load_finanzen():
    data = supabase.table("finanzen").select("*").execute().data
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["datum", "typ", "betrag"])
    df["datum"] = pd.to_datetime(df["datum"], errors="coerce")
    return df

def load_fahrten():
    data = supabase.table("fahrtenbuch").select("*").execute().data
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["datum", "start", "ziel", "kilometer"])
    df["datum"] = pd.to_datetime(df["datum"], errors="coerce")
    return df

belege_df = load_belege()
fin_df = load_finanzen()
fahrten_df = load_fahrten()
settings = load_settings()

# -----------------------------
# JAHR AUSWÄHLEN
# -----------------------------
st.subheader("Jahr auswählen")

jahre = sorted(list(set(belege_df["datum"].dt.year.dropna().astype(int).tolist() +
                        fin_df["datum"].dt.year.dropna().astype(int).tolist() +
                        fahrten_df["datum"].dt.year.dropna().astype(int).tolist())), reverse=True)

if len(jahre) == 0:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

jahr = st.selectbox("Jahr", jahre)

# -----------------------------
# DATEN FILTERN
# -----------------------------
einnahmen = belege_df[(belege_df["typ"] == "Rechnung") & (belege_df["datum"].dt.year == jahr)]
ausgaben = fin_df[(fin_df["typ"] == "Ausgabe") & (fin_df["datum"].dt.year == jahr)]
fahrten = fahrten_df[fahrten_df["datum"].dt.year == jahr]

sum_einnahmen = einnahmen["betrag"].sum()
sum_ausgaben = ausgaben["betrag"].sum()
sum_km = fahrten["kilometer"].astype(float).sum()
km_pauschale = settings.get("km_pauschale", 0.30)
km_betrag = sum_km * km_pauschale
gewinn = sum_einnahmen - sum_ausgaben - km_betrag

# -----------------------------
# PDF ERSTELLEN
# -----------------------------
if st.button("📄 Jahresbericht als PDF erstellen"):

    pdf = PDF()
    pdf.date = datetime.now().strftime("%d.%m.%Y")
    pdf.add_page()

    # Titel
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Jahresbericht {jahr}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "", 12)

    # Kennzahlen
    pdf.cell(0, 8, f"Einnahmen gesamt: {sum_einnahmen:.2f} €", ln=True)
    pdf.cell(0, 8, f"Ausgaben gesamt: {sum_ausgaben:.2f} €", ln=True)
    pdf.cell(0, 8, f"Gefahrene Kilometer: {sum_km:.1f} km", ln=True)
    pdf.cell(0, 8, f"Kilometerpauschale ({km_pauschale:.2f} €): {km_betrag:.2f} €", ln=True)
    pdf.cell(0, 8, f"Gewinn nach Pauschalen: {gewinn:.2f} €", ln=True)

    pdf.ln(10)

    # Einnahmen Tabelle
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Einnahmen", ln=True)
    pdf.set_font("Arial", "", 12)

    for _, row in einnahmen.iterrows():
        pdf.cell(0, 8, f"{row['datum'].strftime('%d.%m.%Y')} – {row['betrag']:.2f} €", ln=True)

    pdf.ln(10)

    # Ausgaben Tabelle
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Ausgaben", ln=True)
    pdf.set_font("Arial", "", 12)

    for _, row in ausgaben.iterrows():
        pdf.cell(0, 8, f"{row['datum'].strftime('%d.%m.%Y')} – {row['betrag']:.2f} €", ln=True)

    pdf.ln(10)

    # Fahrten Tabelle
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Fahrten", ln=True)
    pdf.set_font("Arial", "", 12)

    for _, row in fahrten.iterrows():
        pdf.cell(0, 8, f"{row['datum'].strftime('%d.%m.%Y')} – {row['start']} → {row['ziel']} – {row['kilometer']} km", ln=True)

    # PDF erzeugen
    pdf_bytes = pdf.output(dest="S").encode("latin1")

    # Hochladen
    filename = f"Jahresbericht-{jahr}.pdf"
    pdf_url = upload_pdf_to_supabase(pdf_bytes, filename)

    st.success("Jahresbericht erstellt!")
    st.write("Download-Link:")
    st.write(pdf_url)
