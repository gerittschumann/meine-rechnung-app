import streamlit as st
from utils.db import get_connection

st.set_page_config(
    page_title="📊 Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard")

st.write("""
Überblick über dein Nebengewerbe:
- Anzahl Kunden
- Anzahl Dokumente (Rechnungen, Angebote, Quittungen)
- Gesamtsummen
""")

conn = get_connection()
cur = conn.cursor()

# Kunden zählen
cur.execute("SELECT COUNT(*) AS anzahl FROM kunden")
kunden_count = cur.fetchone()["anzahl"]

# Dokumente zählen
cur.execute("SELECT COUNT(*) AS anzahl FROM dokumente")
dokumente_count = cur.fetchone()["anzahl"]

# Rechnungs-Summe
cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'rechnung'")
rechnungen_summe = cur.fetchone()["summe"]

# Angebote-Summe
cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'angebot'")
angebote_summe = cur.fetchone()["summe"]

# Quittungen-Summe
cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'quittung'")
quittungen_summe = cur.fetchone()["summe"]

conn.close()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 Kunden", kunden_count)
    st.metric("📄 Dokumente gesamt", dokumente_count)

with col2:
    st.metric("📑 Rechnungen – Summe", f"{rechnungen_summe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("📃 Angebote – Summe", f"{angebote_summe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("🧾 Quittungen – Summe", f"{quittungen_summe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.write("---")

st.write("Nutze die Navigation links, um in die einzelnen Bereiche zu wechseln.")
