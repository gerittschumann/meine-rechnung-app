import streamlit as st
from utils.db import get_connection
import pandas as pd
from pathlib import Path
import base64

st.set_page_config(
    page_title="📦 Archiv",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Archiv – Rechnungen, Angebote & Quittungen")

st.write("""
Hier findest du alle gespeicherten Dokumente (Rechnungen, Angebote, Quittungen).
Du kannst die PDFs direkt herunterladen.
""")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# DOKUMENTE LADEN
# ---------------------------------------------------
cur.execute("""
    SELECT 
        d.id,
        d.typ,
        d.nummer,
        d.summe,
        d.pdf_path AS pdf,
        d.erstellt_am,
        k.name AS kunde
    FROM dokumente d
    LEFT JOIN kunden k ON k.id = d.kunde_id
    ORDER BY d.id DESC
""")

daten = cur.fetchall()

if not daten:
    st.info("Noch keine Dokumente im Archiv.")
    st.stop()

# ---------------------------------------------------
# DATEN ALS TABELLE
# ---------------------------------------------------
df = pd.DataFrame(daten)
df.columns = ["ID", "Typ", "Nummer", "Summe (€)", "PDF-Pfad", "Erstellt am", "Kunde"]

st.dataframe(df, use_container_width=True)

st.write("---")
st.subheader("📄 PDF herunterladen")

# ---------------------------------------------------
# PDF DOWNLOAD-BEREICH
# ---------------------------------------------------
for row in daten:
    nummer = row["Nummer"]
    pdf_raw = row["PDF-Pfad"]

    # PDF-Pfad fehlt → überspringen
    if not pdf_raw or str(pdf_raw).strip() == "":
        st.warning(f"⚠️ Kein PDF gespeichert für: {nummer}")
        continue

    pdf_path = Path(pdf_raw)

    # Datei existiert nicht → Hinweis
    if not pdf_path.exists():
        st.error(f"PDF nicht gefunden: {pdf_path}")
        continue

    # PDF laden
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Download-Button
    st.download_button(
        label=f"📄 PDF herunterladen ({nummer})",
        data=pdf_bytes,
        file_name=pdf_path.name,
        mime="application/pdf",
        key=f"download_{row['ID']}"
    )

conn.close()
