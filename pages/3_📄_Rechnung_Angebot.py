import streamlit as st
from utils.db import get_connection, generate_next_number, load_einstellungen
from utils.pdf_generator import generate_pdf
from pathlib import Path
import os

st.set_page_config(
    page_title="📑 Rechnung / Angebot",
    page_icon="📑",
    layout="wide"
)

st.title("📑 Rechnung / Angebot erstellen")

# ---------------------------------------------------
# ARCHIV-PFAD (Persistent Volume auf Railway)
# ---------------------------------------------------
ARCHIV_DIR = Path("/mnt/data/archiv")
ARCHIV_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
einstellungen = load_einstellungen()
if not einstellungen:
    st.warning("⚠️ Bitte zuerst Firmendaten unter 'Einstellungen' eintragen.")
    einstellungen = {}

# ---------------------------------------------------
# FORMULAR
# ---------------------------------------------------
st.subheader("📄 Dokumentdaten")

dokument_typ = st.selectbox("Dokumenttyp", ["rechnung", "angebot"])
kunde_id = st.number_input("Kunden-ID", min_value=1, step=1)

st.write("### 🧾 Positionen")
anzahl = st.number_input("Anzahl Positionen", min_value=1, max_value=20, value=1)

positionen = []
for i in range(anzahl):
    st.write(f"**Position {i+1}**")
    beschreibung = st.text_input(f"Beschreibung {i+1}", key=f"beschr_{i}")
    menge = st.number_input(f"Menge {i+1}", min_value=1.0, value=1.0, key=f"menge_{i}")
    preis = st.number_input(f"Preis {i+1}", min_value=0.0, value=0.0, key=f"preis_{i}")
    gesamt = menge * preis

    positionen.append({
        "beschreibung": beschreibung,
        "menge": menge,
        "preis": preis,
        "gesamt": gesamt
    })

summe = sum(p["gesamt"] for p in positionen)

# ---------------------------------------------------
# PDF VORSCHAU
# ---------------------------------------------------
if st.button("📄 PDF Vorschau erzeugen"):
    dokument = {
        "typ": dokument_typ,
        "kunde_id": kunde_id,
        "nummer": "VORSCHAU",
        "summe": summe
    }

    pdf_bytes = generate_pdf(dokument, positionen, einstellungen)
    st.session_state["pdf_bytes"] = pdf_bytes

# ---------------------------------------------------
# PDF ANZEIGEN
# ---------------------------------------------------
if "pdf_bytes" in st.session_state:
    st.write("### 📄 Vorschau")
    st.download_button(
        "PDF herunterladen",
        data=st.session_state["pdf_bytes"],
        file_name="vorschau.pdf"
    )

    st.write("---")

    # ---------------------------------------------------
    # SPEICHERN
    # ---------------------------------------------------
    if st.button("💾 Dokument speichern"):
        nummer = generate_next_number(dokument_typ)

        # PDF speichern im Railway Persistent Volume
        pdf_path = ARCHIV_DIR / f"{nummer}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(st.session_state["pdf_bytes"])

        # In SQLite speichern
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO dokumente (typ, nummer, kunde_id, pdf_path, summe)
            VALUES (?, ?, ?, ?, ?)
        """, (dokument_typ, nummer, kunde_id, str(pdf_path), summe))

        dokument_id = cur.lastrowid

        for p in positionen:
            cur.execute("""
                INSERT INTO positionen (dokument_id, beschreibung, menge, preis, gesamt)
                VALUES (?, ?, ?, ?, ?)
            """, (dokument_id, p["beschreibung"], p["menge"], p["preis"], p["gesamt"]))

        conn.commit()
        conn.close()

        st.success(f"Dokument gespeichert! Nummer: {nummer}")
