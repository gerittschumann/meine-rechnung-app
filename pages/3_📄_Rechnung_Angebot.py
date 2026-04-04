import streamlit as st
import datetime
import pandas as pd
from utils.db import get_connection, generate_next_number
from utils.pdf_generator import generate_pdf
from utils.pdf_utils import pdf_bytes_to_data_url, save_pdf_to_archiv

st.set_page_config(
    page_title="📄 Rechnung / Angebot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Rechnung & Angebot erstellen")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# Kunden laden
cur.execute("SELECT * FROM kunden ORDER BY name ASC")
kunden = [dict(row) for row in cur.fetchall()]

# Leistungen laden
cur.execute("SELECT * FROM leistungen ORDER BY name ASC")
leistungen = [dict(row) for row in cur.fetchall()]

# Einstellungen laden
cur.execute("SELECT * FROM einstellungen WHERE id = 1")
einstellungen = dict(cur.fetchone()) if cur.fetchone() else {}

# ---------------------------------------------------
# FORMULAR
# ---------------------------------------------------
st.subheader("🧾 Dokumentdaten")

dokument_typ = st.selectbox("Dokumenttyp", ["Rechnung", "Angebot"])
nummer = generate_next_number("rechnung" if dokument_typ == "Rechnung" else "angebot")
datum = st.date_input("Datum", datetime.date.today())

kunde = st.selectbox("Kunde auswählen", kunden, format_func=lambda x: x["name"])

st.write("---")
st.subheader("🛒 Positionen hinzufügen")

if "warenkorb" not in st.session_state:
    st.session_state.warenkorb = []

# Leistung auswählen
auswahl = st.selectbox("Leistung auswählen", leistungen, format_func=lambda x: x["name"])

menge = st.number_input("Menge", min_value=1.0, step=1.0)
preis = st.number_input("Preis überschreiben (optional)", min_value=0.0, step=0.5)

if st.button("➕ Position hinzufügen"):
    st.session_state.warenkorb.append({
        "bezeichnung": auswahl["name"],
        "menge": menge,
        "preis": preis if preis > 0 else auswahl["preis"]
    })
    st.success("Position hinzugefügt.")

# ---------------------------------------------------
# WARENKORB ANZEIGEN
# ---------------------------------------------------
st.write("---")
st.subheader("📦 Warenkorb")

if not st.session_state.warenkorb:
    st.info("Noch keine Positionen hinzugefügt.")
else:
    df = pd.DataFrame(st.session_state.warenkorb)
    df["Summe"] = df["menge"] * df["preis"]
    st.dataframe(df, use_container_width=True)

    gesamt = df["Summe"].sum()
    st.metric("Gesamtbetrag", f"{gesamt:.2f} €")

    if st.button("🗑️ Warenkorb leeren"):
        st.session_state.warenkorb = []
        st.experimental_rerun()

# ---------------------------------------------------
# PDF VORSCHAU
# ---------------------------------------------------
st.write("---")
st.subheader("📄 PDF Vorschau")

if st.session_state.warenkorb:
    if st.button("📄 Vorschau anzeigen"):
        pdf_bytes = generate_pdf(
            {
                "dokument_typ": dokument_typ,
                "nummer": nummer,
                "datum": datum.isoformat(),
                "text_rechnung": einstellungen.get("text_rechnung", "") if dokument_typ == "Rechnung" else einstellungen.get("text_angebot", "")
            },
            kunde,
            einstellungen,
            st.session_state.warenkorb
        )

        pdf_url = pdf_bytes_to_data_url(pdf_bytes)
        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

# ---------------------------------------------------
# SPEICHERN
# ---------------------------------------------------
st.write("---")
st.subheader("💾 Dokument speichern")

if st.session_state.warenkorb:
    if st.button("💾 Speichern & PDF archivieren"):
        pdf_bytes = generate_pdf(
            {
                "dokument_typ": dokument_typ,
                "nummer": nummer,
                "datum": datum.isoformat(),
                "text_rechnung": einstellungen.get("text_rechnung", "") if dokument_typ == "Rechnung" else einstellungen.get("text_angebot", "")
            },
            kunde,
            einstellungen,
            st.session_state.warenkorb
        )

        # PDF archivieren
        pdf_path = save_pdf_to_archiv(pdf_bytes, nummer)

        # Dokument speichern
        cur.execute("""
            INSERT INTO dokumente (typ, nummer, kunde_id, pdf_path, summe)
            VALUES (?, ?, ?, ?, ?)
        """, (
            dokument_typ.lower(),
            nummer,
            kunde["id"],
            str(pdf_path),
            gesamt
        ))
        conn.commit()

        # Positionen speichern
        for pos in st.session_state.warenkorb:
            cur.execute("""
                INSERT INTO positionen (dokument_id, beschreibung, menge, preis, gesamt)
                VALUES ((SELECT id FROM dokumente WHERE nummer = ?), ?, ?, ?, ?)
            """, (
                nummer,
                pos["bezeichnung"],
                pos["menge"],
                pos["preis"],
                pos["menge"] * pos["preis"]
            ))
        conn.commit()

        st.success("Dokument gespeichert & PDF archiviert.")
        st.session_state.warenkorb = []
        st.experimental_rerun()

conn.close()
