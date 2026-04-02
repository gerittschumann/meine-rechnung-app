import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="⚙️ Einstellungen",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Einstellungen")

st.write("""
Hier kannst du deine Firmendaten und die Standardtexte für:
- Rechnungen
- Angebote
- Quittungen  
festlegen und speichern.
""")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM einstellungen WHERE id = 1")
row = cur.fetchone()

firma_name = row["firma_name"] if row else ""
firma_adresse = row["firma_adresse"] if row else ""
firma_plz = row["firma_plz"] if row else ""
firma_ort = row["firma_ort"] if row else ""
steuernummer = row["steuernummer"] if row else ""
iban = row["iban"] if row else ""
bic = row["bic"] if row else ""

# Neue Felder:
text_rechnung = row["text_rechnung"] if row and "text_rechnung" in row.keys() else ""
text_angebot = row["text_angebot"] if row and "text_angebot" in row.keys() else ""
text_quittung = row["text_quittung"] if row and "text_quittung" in row.keys() else ""

# ---------------------------------------------------
# FORMULAR
# ---------------------------------------------------
st.subheader("🏢 Firmendaten")

with st.form("einstellungen_form"):
    firma_name = st.text_input("Firmenname", value=firma_name)
    firma_adresse = st.text_input("Adresse", value=firma_adresse)
    firma_plz = st.text_input("PLZ", value=firma_plz)
    firma_ort = st.text_input("Ort", value=firma_ort)
    steuernummer = st.text_input("Steuernummer", value=steuernummer)
    iban = st.text_input("IBAN", value=iban)
    bic = st.text_input("BIC", value=bic)

    st.write("---")
    st.subheader("📝 Standardtexte für Dokumente")

    text_rechnung = st.text_area(
        "Text für Rechnungen",
        value=text_rechnung,
        placeholder="z. B.: Bitte begleichen Sie den Betrag innerhalb von 7 Tagen."
    )

    text_angebot = st.text_area(
        "Text für Angebote",
        value=text_angebot,
        placeholder="z. B.: Vielen Dank für Ihre Anfrage."
    )

    text_quittung = st.text_area(
        "Text für Quittungen",
        value=text_quittung,
        placeholder="z. B.: Vielen Dank für Ihren Auftrag, ich habe den Betrag dankend erhalten."
    )

    submitted = st.form_submit_button("Speichern")

    if submitted:
        # Tabelle erweitern, falls Felder fehlen
        cur.execute("PRAGMA table_info(einstellungen)")
        columns = [c[1] for c in cur.fetchall()]

        if "text_rechnung" not in columns:
            cur.execute("ALTER TABLE einstellungen ADD COLUMN text_rechnung TEXT")
        if "text_angebot" not in columns:
            cur.execute("ALTER TABLE einstellungen ADD COLUMN text_angebot TEXT")
        if "text_quittung" not in columns:
            cur.execute("ALTER TABLE einstellungen ADD COLUMN text_quittung TEXT")

        # Alte Einstellungen löschen
        cur.execute("DELETE FROM einstellungen WHERE id = 1")

        # Neue speichern
        cur.execute("""
            INSERT INTO einstellungen (
                id, firma_name, firma_adresse, firma_plz, firma_ort,
                steuernummer, iban, bic,
                text_rechnung, text_angebot, text_quittung
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            firma_name, firma_adresse, firma_plz, firma_ort,
            steuernummer, iban, bic,
            text_rechnung, text_angebot, text_quittung
        ))

        conn.commit()
        st.success("Einstellungen gespeichert!")

conn.close()
