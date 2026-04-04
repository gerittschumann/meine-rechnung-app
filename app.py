import streamlit as st
from utils.db import init_db

init_db()

# ---------------------------------------------------
# GRUNDEINSTELLUNGEN
# ---------------------------------------------------
st.set_page_config(
    page_title="Nebengewerbe – Verwaltung",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# DATENBANK INITIALISIEREN
# ---------------------------------------------------
init_db()

# ---------------------------------------------------
# STARTSEITE / DASHBOARD
# ---------------------------------------------------
st.title("📊 Dashboard")

st.write("""
Willkommen in deiner Verwaltungs-App für dein Nebengewerbe.

Über die Navigation links kannst du:
- Kunden verwalten
- Rechnungen und Angebote erstellen
- Quittungen erfassen
- Fahrtenbuch führen
- Finanzen und Jahresberichte einsehen
- Einstellungen für Firmendaten pflegen
- Archivierte Dokumente ansehen
""")

st.write("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👥 Kunden")
    st.write("Verwalte deine Kundenstammdaten.")
    st.write("➡️ Seite: **2_🧍_Kunden**")

with col2:
    st.subheader("📑 Rechnungen & Angebote")
    st.write("Erstelle und verwalte Rechnungen und Angebote.")
    st.write("➡️ Seite: **3_📑_Rechnung_Angebot**")

with col3:
    st.subheader("📦 Archiv")
    st.write("Alle erzeugten Dokumente im Überblick.")
    st.write("➡️ Seite: **8_📦_Archiv**")

st.write("---")

st.info("Hinweis: Die Daten werden in einer lokalen SQLite-Datenbank (`database.db`) gespeichert. PDFs liegen im Archiv-Ordner auf dem Server.")
