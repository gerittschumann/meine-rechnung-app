import streamlit as st
from utils.db import get_connection
from utils.pdf_generator import generate_pdf
import pandas as pd
import base64
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="🧾 Quittung erstellen",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Quittung zu einer bestehenden Rechnung erstellen")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# RECHNUNGEN LADEN
# ---------------------------------------------------
cur.execute("""
    SELECT d.id, d.nummer, k.name AS kunde
    FROM dokumente d
    LEFT JOIN kunden k ON d.kunde_id = k.id
    WHERE d.typ = 'rechnung'
    ORDER BY d.id DESC
""")
rechnungen = cur.fetchall()

if not rechnungen:
    st.warning("⚠️ Es existieren noch keine Rechnungen.")
    st.stop()

rechnungs_liste = [f"{r['id']} – {r['nummer']} – {r['kunde']}" for r in rechnungen]
auswahl = st.selectbox("Rechnung auswählen", rechnungs_liste)

rechnung_id = int(auswahl.split(" – ")[0])

# ---------------------------------------------------
# RECHNUNGSDATEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM dokumente WHERE id = ?", (rechnung_id,))
rechnung = cur.fetchone()

cur.execute("SELECT * FROM positionen WHERE dokument_id = ?", (rechnung_id,))
positionen = cur.fetchall()

cur.execute("""
    SELECT k.*
    FROM kunden k
    JOIN dokumente d ON d.kunde_id = k.id
    WHERE d.id = ?
""", (rechnung_id,))
kunde = cur.fetchone()

# ---------------------------------------------------
# QUITTUNGSNUMMER
# ---------------------------------------------------
quittungsnummer = f"{rechnung['nummer']}-Q"
st.write(f"**Quittungsnummer:** {quittungsnummer}")

# ---------------------------------------------------
# SIGNATURFELD
# ---------------------------------------------------
st.subheader("✍️ Unterschrift erfassen")

signature = st_canvas(
    fill_color="rgba(0, 0, 0, 1)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=200,
    width=600,
    drawing_mode="freedraw",
    key="canvas_quittung",
)

signature_png = None
if signature.image_data is not None:
    signature_png = signature.image_data

# ---------------------------------------------------
# PDF-VORSCHAU (NICHT SPEICHERN)
# ---------------------------------------------------
st.write("---")
st.subheader("👁️ Vorschau anzeigen (ohne Speichern)")

if st.button("Vorschau anzeigen"):
    if signature_png is None:
        st.error("Bitte unterschreiben, bevor du die Vorschau anzeigen kannst.")
        st.stop()

    pdf_bytes = generate_pdf(
        {
            "typ": "quittung",
            "nummer": quittungsnummer,
            "kunde": kunde,
            "rechnung": rechnung,
            "signatur": signature_png,
            "preview": True
        },
        positionen,
        {}
    )

    b64 = base64.b64encode(pdf_bytes).decode()
    iframe = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900px"></iframe>'
    st.markdown(iframe, unsafe_allow_html=True)

# ---------------------------------------------------
# QUITTUNG FINAL SPEICHERN
# ---------------------------------------------------
st.write("---")
st.subheader("📄 Quittung final erstellen")

if st.button("Quittung speichern"):
    if signature_png is None:
        st.error("Bitte unterschreiben, bevor du die Quittung speichern kannst.")
        st.stop()

    # Quittung speichern
    cur.execute("""
        INSERT INTO dokumente (typ, nummer, kunde_id, summe)
        VALUES ('quittung', ?, ?, ?)
    """, (quittungsnummer, kunde["id"], rechnung["summe"]))
    conn.commit()

    # Neue Quittungs-ID holen
    cur.execute("SELECT id FROM dokumente ORDER BY id DESC LIMIT 1")
    quittung_id = cur.fetchone()["id"]

    st.success("Quittung erfolgreich erstellt!")
    st.balloons()

conn.close()
