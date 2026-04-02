import streamlit as st
from utils.db import get_connection, generate_next_number, load_einstellungen
from utils.pdf_generator import generate_pdf
from pathlib import Path

st.set_page_config(
    page_title="🧾 Quittung",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Quittung erstellen")

# ---------------------------------------------------
# ARCHIV-PFAD (Railway Persistent Volume)
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
st.subheader("📄 Quittungsdaten")

kunde_id = st.number_input("Kunden-ID", min_value=1, step=1)
betrag = st.number_input("Betrag (€)", min_value=0.0, value=0.0, step=0.5)
beschreibung = st.text_area("Beschreibung / Zweck der Zahlung")

# ---------------------------------------------------
# PDF VORSCHAU
# ---------------------------------------------------
if st.button("📄 PDF Vorschau erzeugen"):
    dokument = {
        "typ": "quittung",
        "kunde_id": kunde_id,
        "nummer": "VORSCHAU",
        "summe": betrag
    }

    positionen = [{
        "beschreibung": beschreibung if beschreibung else "Zahlung",
        "menge": 1,
        "preis": betrag,
        "gesamt": betrag
    }]

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
        file_name="quittung_vorschau.pdf"
    )

    st.write("---")

    # ---------------------------------------------------
    # SPEICHERN
    # ---------------------------------------------------
    if st.button("💾 Quittung speichern"):
        nummer = generate_next_number("quittung")

        # PDF speichern im Railway Volume
        pdf_path = ARCHIV_DIR / f"{nummer}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(st.session_state["pdf_bytes"])

        # In SQLite speichern
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO dokumente (typ, nummer, kunde_id, pdf_path, summe)
            VALUES (?, ?, ?, ?, ?)
        """, ("quittung", nummer, kunde_id, str(pdf_path), betrag))

        dokument_id = cur.lastrowid

        # Position speichern
        cur.execute("""
            INSERT INTO positionen (dokument_id, beschreibung, menge, preis, gesamt)
            VALUES (?, ?, ?, ?, ?)
        """, (dokument_id, beschreibung if beschreibung else "Zahlung", 1, betrag, betrag))

        conn.commit()
        conn.close()

        st.success(f"Quittung gespeichert! Nummer: {nummer}")
