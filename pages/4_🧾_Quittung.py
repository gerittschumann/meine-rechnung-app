import streamlit as st
from utils.db import get_connection
from utils.pdf_generator import generate_pdf
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
    SELECT d.id, d.nummer, d.summe, k.name AS kunde, k.id AS kunde_id
    FROM dokumente d
    LEFT JOIN kunden k ON d.kunde_id = k.id
    WHERE d.typ = 'rechnung'
    ORDER BY d.id DESC
""")
rechnungen = [dict(r) for r in cur.fetchall()]

if not rechnungen:
    st.warning("⚠️ Es existieren noch keine Rechnungen.")
    st.stop()

rechnungs_liste = [f"{r['id']} – {r['nummer']} – {r['kunde']}" for r in rechnungen]
auswahl = st.selectbox("Rechnung auswählen", rechnungs_liste)

rechnung_id = int(auswahl.split(" – ")[0])
rechnung = next(r for r in rechnungen if r["id"] == rechnung_id)

# ---------------------------------------------------
# POSITIONEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM positionen WHERE dokument_id = ?", (rechnung_id,))
positionen = [dict(p) for p in cur.fetchall()]

# ---------------------------------------------------
# KUNDENDATEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM kunden WHERE id = ?", (rechnung["kunde_id"],))
kunde_row = cur.fetchone()
kunde = dict(kunde_row) if kunde_row else {}

# ---------------------------------------------------
# FIRMENDATEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM einstellungen WHERE id = 1")
firma_row = cur.fetchone()
firma = dict(firma_row) if firma_row else {}

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

signature_png = signature.image_data if signature.image_data is not None else None

# ---------------------------------------------------
# PDF-VORSCHAU
# ---------------------------------------------------
st.write("---")
st.subheader("👁️ Vorschau anzeigen (ohne Speichern)")

if st.button("Vorschau anzeigen"):
    if signature_png is None:
        st.error("Bitte unterschreiben, bevor du die Vorschau anzeigen kannst.")
        st.stop()

    eintrag = {
        "dokument_typ": "Quittung",
        "nummer": quittungsnummer,
        "datum": "",
        "text_rechnung": "Quittung zur Rechnung " + rechnung["nummer"],
        "signatur": signature_png
    }

    pdf_bytes = generate_pdf(
        eintrag,
        kunde,
        firma,
        positionen
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

    cur.execute("""
        INSERT INTO dokumente (typ, nummer, kunde_id, summe)
        VALUES ('quittung', ?, ?, ?)
    """, (quittungsnummer, kunde["id"], rechnung["summe"]))
    conn.commit()

    st.success("Quittung erfolgreich erstellt!")
    st.balloons()

conn.close()
