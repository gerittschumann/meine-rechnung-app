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

# ---------------------------------------------------
# DATENBANKVERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# KUNDEN ZÄHLEN
# ---------------------------------------------------
cur.execute("SELECT COUNT(*) AS anzahl FROM kunden")
row = cur.fetchone()
kunden_count = row["anzahl"] if row else 0

# ---------------------------------------------------
# DOKUMENTE ZÄHLEN
# ---------------------------------------------------
cur.execute("SELECT COUNT(*) AS anzahl FROM dokumente")
row = cur.fetchone()
dokumente_count = row["anzahl"] if row else 0

# ---------------------------------------------------
# SUMMEN LADEN
# ---------------------------------------------------
def get_sum(typ):
    cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = ?", (typ,))
    row = cur.fetchone()
    return row["summe"] if row else 0

rechnungen_summe = get_sum("rechnung")
angebote_summe = get_sum("angebot")
quittungen_summe = get_sum("quittung")

conn.close()

# ---------------------------------------------------
# UI – METRICS
# ---------------------------------------------------
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
