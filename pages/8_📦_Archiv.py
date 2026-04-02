import streamlit as st
from utils.db import get_connection
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="📦 Archiv",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Archiv – Alle gespeicherten Dokumente")

# ---------------------------------------------------
# ARCHIV-PFAD (Railway Persistent Volume)
# ---------------------------------------------------
ARCHIV_DIR = Path("/mnt/data/archiv")
ARCHIV_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------
# DATEN LADEN
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT 
        id,
        typ,
        nummer,
        kunde_id,
        summe,
        pdf_path,
        erstellt_am
    FROM dokumente
    ORDER BY erstellt_am DESC
""")
dokumente = cur.fetchall()

conn.close()

# ---------------------------------------------------
# FILTER
# ---------------------------------------------------
st.subheader("🔍 Filter")

col1, col2, col3 = st.columns(3)

with col1:
    typ_filter = st.selectbox("Dokumenttyp", ["Alle", "rechnung", "angebot", "quittung"])

with col2:
    jahr_filter = st.selectbox(
        "Jahr",
        ["Alle"] + sorted(list({d["erstellt_am"][:4] for d in dokumente}))
    )

with col3:
    kunde_filter = st.text_input("Kunden-ID (optional)")

# ---------------------------------------------------
# DATEN AUFBEREITEN
# ---------------------------------------------------
if not dokumente:
    st.info("Noch keine Dokumente gespeichert.")
else:
    df = pd.DataFrame(dokumente)
    df.columns = ["ID", "Typ", "Nummer", "Kunden-ID", "Summe (€)", "PDF-Pfad", "Erstellt am"]

    # Filter anwenden
    if typ_filter != "Alle":
        df = df[df["Typ"] == typ_filter]

    if jahr_filter != "Alle":
        df = df[df["Erstellt am"].str.startswith(jahr_filter)]

    if kunde_filter.strip() != "":
        df = df[df["Kunden-ID"].astype(str) == kunde_filter.strip()]

    st.dataframe(df, use_container_width=True)

    st.write("---")

    # ---------------------------------------------------
    # PDF DOWNLOAD
    # ---------------------------------------------------
    st.subheader("📄 PDF herunterladen")

    if len(df) == 0:
        st.info("Keine Dokumente für den aktuellen Filter gefunden.")
    else:
        # Auswahl
        auswahl = st.selectbox(
            "Dokument auswählen",
            df["Nummer"].tolist()
        )

        # Pfad ermitteln
        row = df[df["Nummer"] == auswahl].iloc[0]
        pdf_path = Path(row["PDF-Pfad"])

        if not pdf_path.exists():
            st.error("PDF-Datei wurde nicht gefunden.")
        else:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label=f"📥 PDF herunterladen ({auswahl})",
                data=pdf_bytes,
                file_name=f"{auswahl}.pdf",
                mime="application/pdf"
            )
