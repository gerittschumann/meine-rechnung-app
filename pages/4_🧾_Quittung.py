import streamlit as st
import datetime
import pandas as pd
import base64

from utils.db import get_connection, generate_next_number
from utils.pdf_generator import generate_pdf
from utils.pdf_utils import pdf_bytes_to_data_url, save_pdf_to_archiv

try:
    from streamlit_signature_pad import st_signature_pad
    SIGNATURE_AVAILABLE = True
except Exception:
    SIGNATURE_AVAILABLE = False

st.set_page_config(
    page_title="🧾 Quittung",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Quittung erstellen")

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
row = cur.fetchone()
einstellungen = dict(row) if row else {}

# ---------------------------------------------------
# FORMULAR BASISDATEN
# ---------------------------------------------------
st.subheader("🧾 Quittungsdaten")

nummer = generate_next_number("quittung")
datum = st.date_input("Datum", datetime.date.today())

kunde = st.selectbox("Kunde auswählen", kunden, format_func=lambda x: x["name"])

st.write("---")
st.subheader("🛒 Positionen hinzufügen")

if "warenkorb_quittung" not in st.session_state:
    st.session_state.warenkorb_quittung = []

# Leistung auswählen
auswahl = st.selectbox("Leistung auswählen", leistungen, format_func=lambda x: x["name"])

menge = st.number_input("Menge", min_value=1.0, step=1.0, key="menge_quittung")
preis = st.number_input("Preis überschreiben (optional)", min_value=0.0, step=0.5, key="preis_quittung")

if st.button("➕ Position hinzufügen", key="add_pos_quittung"):
    st.session_state.warenkorb_quittung.append({
        "bezeichnung": auswahl["name"],
        "menge": menge,
        "preis": preis if preis > 0 else auswahl["preis"]
    })
    st.success("Position hinzugefügt.")

# ---------------------------------------------------
# WARENKORB
# ---------------------------------------------------
st.write("---")
st.subheader("📦 Warenkorb")

if not st.session_state.warenkorb_quittung:
    st.info("Noch keine Positionen hinzugefügt.")
    gesamt = 0.0
else:
    df = pd.DataFrame(st.session_state.warenkorb_quittung)
    df["Summe"] = df["menge"] * df["preis"]
    st.dataframe(df, use_container_width=True)

    gesamt = df["Summe"].sum()
    st.metric("Gesamtbetrag", f"{gesamt:.2f} €")

    if st.button("🗑️ Warenkorb leeren", key="clear_cart_quittung"):
        st.session_state.warenkorb_quittung = []
        st.experimental_rerun()

# ---------------------------------------------------
# UNTERSCHRIFT
# ---------------------------------------------------
st.write("---")
st.subheader("✍️ Unterschrift")

signatur_bytes = None

if not SIGNATURE_AVAILABLE:
    st.warning("Signatur-Pad ist nicht verfügbar. (Paket 'streamlit_signature_pad' nicht installiert?)")
else:
    sig_data = st_signature_pad(
        background_color="white",
        pen_color="black",
        key="signature_quittung"
    )
    if sig_data:
        try:
            header, b64data = sig_data.split(",")
            signatur_bytes = base64.b64decode(b64data)
            st.success("Unterschrift erfasst.")
        except Exception:
            st.error("Unterschrift konnte nicht verarbeitet werden.")

# ---------------------------------------------------
# PDF VORSCHAU
# ---------------------------------------------------
st.write("---")
st.subheader("📄 PDF Vorschau")

if st.session_state.warenkorb_quittung:
    if st.button("📄 Vorschau anzeigen", key="preview_quittung"):
        eintrag = {
            "dokument_typ": "Quittung",
            "nummer": nummer,
            "datum": datum.isoformat(),
            "text_rechnung": einstellungen.get("text_quittung", "")
        }

        pdf_bytes = generate_pdf(
            eintrag,
            kunde,
            einstellungen,
            st.session_state.warenkorb_quittung,
            signatur_bytes=signatur_bytes
        )

        pdf_url = pdf_bytes_to_data_url(pdf_bytes)
        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

# ---------------------------------------------------
# SPEICHERN
# ---------------------------------------------------
st.write("---")
st.subheader("💾 Quittung speichern")

if st.session_state.warenkorb_quittung:
    if st.button("💾 Speichern & PDF archivieren", key="save_quittung"):
        eintrag = {
            "dokument_typ": "Quittung",
            "nummer": nummer,
            "datum": datum.isoformat(),
            "text_rechnung": einstellungen.get("text_quittung", "")
        }

        pdf_bytes = generate_pdf(
            eintrag,
            kunde,
            einstellungen,
            st.session_state.warenkorb_quittung,
            signatur_bytes=signatur_bytes
        )

        # PDF archivieren
        pdf_path = save_pdf_to_archiv(pdf_bytes, nummer)

        # Dokument speichern
        cur.execute("""
            INSERT INTO dokumente (typ, nummer, kunde_id, pdf_path, summe)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "quittung",
            nummer,
            kunde["id"],
            str(pdf_path),
            gesamt
        ))
        conn.commit()

        # Positionen speichern
        for pos in st.session_state.warenkorb_quittung:
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

        st.success("Quittung gespeichert & PDF archiviert.")
        st.session_state.warenkorb_quittung = []
        st.experimental_rerun()

conn.close()
