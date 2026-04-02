import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="💰 Finanzen",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Finanzübersicht")

# ---------------------------------------------------
# DATEN LADEN
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# Gesamtsummen
cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'rechnung'")
sum_rechnungen = cur.fetchone()["summe"]

cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'quittung'")
sum_quittungen = cur.fetchone()["summe"]

cur.execute("SELECT IFNULL(SUM(summe), 0) AS summe FROM dokumente WHERE typ = 'angebot'")
sum_angebote = cur.fetchone()["summe"]

# Monatsübersicht
cur.execute("""
    SELECT 
        strftime('%Y-%m', erstellt_am) AS monat,
        SUM(CASE WHEN typ = 'rechnung' THEN summe ELSE 0 END) AS rechnungen,
        SUM(CASE WHEN typ = 'quittung' THEN summe ELSE 0 END) AS quittungen,
        SUM(CASE WHEN typ = 'angebot' THEN summe ELSE 0 END) AS angebote
    FROM dokumente
    GROUP BY monat
    ORDER BY monat DESC
""")
monatsdaten = cur.fetchall()

# Gesamte Dokumentliste
cur.execute("""
    SELECT id, typ, nummer, kunde_id, summe, erstellt_am
    FROM dokumente
    ORDER BY erstellt_am DESC
""")
dokumente = cur.fetchall()

conn.close()

# ---------------------------------------------------
# KENNZAHLEN
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📑 Rechnungen – Einnahmen", f"{sum_rechnungen:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col2:
    st.metric("🧾 Quittungen – Einnahmen", f"{sum_quittungen:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("📃 Angebote – Gesamtwert", f"{sum_angebote:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.write("---")

# ---------------------------------------------------
# MONATSÜBERSICHT
# ---------------------------------------------------
st.subheader("📅 Monatsübersicht")

if not monatsdaten:
    st.info("Noch keine Daten vorhanden.")
else:
    df_monate = pd.DataFrame(monatsdaten)
    df_monate.columns = ["Monat", "Rechnungen (€)", "Quittungen (€)", "Angebote (€)"]

    st.dataframe(df_monate, use_container_width=True)

st.write("---")

# ---------------------------------------------------
# DOKUMENTLISTE
# ---------------------------------------------------
st.subheader("📄 Alle Dokumente")

if not dokumente:
    st.info("Noch keine Dokumente vorhanden.")
else:
    df_docs = pd.DataFrame(dokumente)
    df_docs.columns = ["ID", "Typ", "Nummer", "Kunden-ID", "Summe (€)", "Erstellt am"]

    st.dataframe(df_docs, use_container_width=True)
