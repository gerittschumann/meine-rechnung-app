import streamlit as st
from utils.db import get_connection, generate_next_number
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64
import datetime
from utils.pdf_utils import create_quittung_pdf, ARCHIV_DIR

st.title("🧾 Quittung erstellen")

conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# RECHNUNG AUSWÄHLEN
# ---------------------------------------------------
st.subheader("Rechnung auswählen")

cur.execute("""
    SELECT id, nummer, kunde_id, summe
    FROM dokumente
    WHERE typ = 'Rechnung'
    ORDER BY id DESC
""")
rechnungen = cur.fetchall()

if not rechnungen:
    st.warning("Es existieren noch keine Rechnungen. Bitte zuerst eine Rechnung erstellen.")
    st.stop()

auswahl = st.selectbox(
    "Bitte Rechnung auswählen",
    options=rechnungen,
    format_func=lambda x: f"{x['nummer']} – {x['summe']} €"
)

rechnung_id = auswahl["id"]
rechnung_nummer = auswahl["nummer"]
kunde_id = auswahl["kunde_id"]
betrag = auswahl["summe"]

# Kundendaten laden
cur.execute("SELECT * FROM kunden WHERE id = ?", (kunde_id,))
kunde = cur.fetchone()

st.write(f"**Kunde:** {kunde['name']}")
st.write(f"**Betrag:** {betrag} €")
st.write(f"**Rechnungsnummer:** {rechnung_nummer}")

st.write("---")

# ---------------------------------------------------
# WARENKORB / POSITIONEN
# ---------------------------------------------------
st.subheader("Positionen für die Quittung")

if "warenkorb_quittung" not in st.session_state:
    st.session_state.warenkorb_quittung = []

beschreibung = st.text_input("Beschreibung")
preis = st.number_input("Preis (€)", min_value=0.0, step=0.5)

if st.button("➕ Position hinzufügen"):
    if beschreibung and preis > 0:
        st.session_state.warenkorb_quittung.append({
            "beschreibung": beschreibung,
            "menge": 1,
            "preis": preis,
            "gesamt": preis
        })
    else:
        st.error("Bitte Beschreibung und Preis eingeben.")

# Warenkorb anzeigen
for i, pos in enumerate(st.session_state.warenkorb_quittung):
    st.write(f"{i+1}. {pos['beschreibung']} – {pos['preis']} €")

if st.button("🧾 Warenkorb leeren"):
    st.session_state.warenkorb_quittung = []
    st.experimental_rerun()

st.write("---")

# ---------------------------------------------------
# SIGNATUR
# ---------------------------------------------------
st.subheader("✍️ Unterschrift")

signatur_bytes = None

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=200,
    width=500,
    drawing_mode="freedraw",
    key="signature_quittung_canvas",
)

if canvas_result.image_data is not None:
    signature_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
    buffer = io.BytesIO()
    signature_image.save(buffer, format="PNG")
    signatur_bytes = buffer.getvalue()
    st.image(signature_image, caption="Ihre Unterschrift")

st.write("---")

# ---------------------------------------------------
# PDF VORSCHAU
# ---------------------------------------------------
st.subheader("📄 PDF Vorschau")

if st.session_state.warenkorb_quittung:
    if st.button("🧾 Vorschau anzeigen"):
        quittungsnummer = generate_next_number("Quittung")
        pdf_bytes = create_quittung_pdf(
            quittungsnummer,
            kunde,
            st.session_state.warenkorb_quittung,
            signatur_bytes,
            rechnung_nummer
        )
        st.download_button(
            "PDF herunterladen",
            data=pdf_bytes,
            file_name=f"{quittungsnummer}.pdf",
            mime="application/pdf"
        )
else:
    st.info("Bitte Positionen hinzufügen.")

st.write("---")

# ---------------------------------------------------
# QUITTUNG SPEICHERN
# ---------------------------------------------------
st.subheader("💾 Quittung speichern")

if st.button("Quittung endgültig erstellen"):
    if not st.session_state.warenkorb_quittung:
        st.error("Bitte Positionen hinzufügen.")
        st.stop()

    if not signatur_bytes:
        st.error("Bitte unterschreiben.")
        st.stop()

    quittungsnummer = generate_next_number("Quittung")

    # PDF erzeugen
    pdf_bytes = create_quittung_pdf(
        quittungsnummer,
        kunde,
        st.session_state.warenkorb_quittung,
        signatur_bytes,
        rechnung_nummer
    )

    # PDF speichern
    pdf_path = ARCHIV_DIR / f"{quittungsnummer}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    # Dokument speichern
    cur.execute("""
        INSERT INTO dokumente (typ, nummer, kunde_id, pdf_path, summe)
        VALUES (?, ?, ?, ?, ?)
    """, ("Quittung", quittungsnummer, kunde_id, str(pdf_path), betrag))
    quittung_id = cur.lastrowid

    # Positionen speichern
    for pos in st.session_state.warenkorb_quittung:
        cur.execute("""
            INSERT INTO positionen (dokument_id, beschreibung, menge, preis, gesamt)
            VALUES (?, ?, ?, ?, ?)
        """, (quittung_id, pos["beschreibung"], pos["menge"], pos["preis"], pos["gesamt"]))

    conn.commit()

    st.success(f"Quittung {quittungsnummer} wurde erfolgreich erstellt.")
    st.session_state.warenkorb_quittung = []
