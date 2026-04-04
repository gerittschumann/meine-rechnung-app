import streamlit as st
import sqlite3
from utils.db import get_connection
from utils.pdf_generator import generate_pdf

st.set_page_config(page_title="📄 Rechnung / Angebot", page_icon="📄")

st.title("📄 Rechnung / Angebot erstellen")

# ---------------------------------------------------
# DATENBANKVERBINDUNG
# ---------------------------------------------------
conn = get_connection()
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ---------------------------------------------------
# KUNDEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM kunden ORDER BY name ASC")
kunden = [dict(row) for row in cur.fetchall()]

# ---------------------------------------------------
# FIRMENDATEN LADEN (aus einstellungen)
# ---------------------------------------------------
cur.execute("SELECT * FROM einstellungen WHERE id = 1")
firma_row = cur.fetchone()
firma = dict(firma_row) if firma_row else {}

# ---------------------------------------------------
# LEISTUNGSKATALOG LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM leistungen ORDER BY name ASC")
leistungs_katalog = [dict(row) for row in cur.fetchall()]

# ---------------------------------------------------
# FORMULAR: DOKUMENTTYP
# ---------------------------------------------------
dokument_typ = st.selectbox("Dokumenttyp", ["Rechnung", "Angebot"])

# ---------------------------------------------------
# FORMULAR: KUNDE
# ---------------------------------------------------
kunden_namen = [k["name"] for k in kunden]
kunde_auswahl = st.selectbox("Kunde auswählen", kunden_namen)

kunde = next((k for k in kunden if k["name"] == kunde_auswahl), None)

# ---------------------------------------------------
# FORMULAR: NUMMER & DATUM
# ---------------------------------------------------
nummer = st.text_input("Nummer", "")
datum = st.date_input("Datum")

# ---------------------------------------------------
# FORMULAR: TEXTBLOCK
# ---------------------------------------------------
text_rechnung = st.text_area("Textblock (optional)", "")

# ---------------------------------------------------
# FORMULAR: LEISTUNGEN
# ---------------------------------------------------
st.subheader("Leistungen hinzufügen")

positionen = []
for i in range(1, 11):
    col1, col2, col3 = st.columns([4, 1, 2])

    with col1:
        bez = st.selectbox(
            f"Leistung {i}",
            [""] + [l["name"] for l in leistungs_katalog],
            key=f"bez_{i}"
        )

    with col2:
        menge = st.number_input(f"Menge {i}", min_value=0.0, value=0.0, key=f"menge_{i}")

    with col3:
        preis = st.number_input(f"Preis {i}", min_value=0.0, value=0.0, key=f"preis_{i}")

    if bez and menge > 0:
        # passende Leistung aus Katalog holen
        leistung = next((l for l in leistungs_katalog if l["name"] == bez), None)

        positionen.append({
            "bezeichnung": bez,
            "menge": menge,
            "preis": preis if preis > 0 else (leistung["preis"] if leistung else 0)
        })

# ---------------------------------------------------
# PDF ERZEUGEN
# ---------------------------------------------------
if st.button("PDF erzeugen"):
    if not kunde:
        st.error("Bitte einen Kunden auswählen.")
    else:
        eintrag = {
            "dokument_typ": dokument_typ,
            "nummer": nummer,
            "datum": str(datum),
            "text_rechnung": text_rechnung
        }

        pdf_bytes = generate_pdf(
            eintrag,
            kunde,
            firma,
            positionen
        )

        st.success("PDF erfolgreich erzeugt!")
        st.download_button(
            label="PDF herunterladen",
            data=pdf_bytes,
            file_name=f"{dokument_typ}_{nummer}.pdf",
            mime="application/pdf"
        )
