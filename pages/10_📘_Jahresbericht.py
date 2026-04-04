import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="📘 Jahresbericht",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Jahresbericht")

st.write("""
Dieser Jahresbericht fasst alle wichtigen Kennzahlen zusammen:
- Umsätze aus Rechnungen
- Einnahmen aus Quittungen
- Angebotsvolumen
- Fahrtenbuch-Kilometer
- Monats- und Jahresübersichten
""")

# ---------------------------------------------------
# DATEN LADEN
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# Dokumente pro Jahr
cur.execute("""
    SELECT 
        strftime('%Y', erstellt_am) AS jahr,
        strftime('%m', erstellt_am) AS monat,
        typ,
        summe
    FROM dokumente
""")
docs = [dict(row) for row in cur.fetchall()]

# Fahrtenbuch pro Jahr
cur.execute("""
    SELECT 
        strftime('%Y', datum) AS jahr,
        strftime('%m', datum) AS monat,
        km_diff
    FROM fahrtenbuch
""")
fahrten = [dict(row) for row in cur.fetchall()]

conn.close()

# ---------------------------------------------------
# DATEN AUFBEREITEN
# ---------------------------------------------------
if not docs and not fahrten:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

df_docs = pd.DataFrame(docs, columns=["Jahr", "Monat", "Typ", "Summe"])
df_fahrten = pd.DataFrame(fahrten, columns=["Jahr", "Monat", "KM"])

# Jahr-Auswahl
jahre = sorted(list(set(df_docs["Jahr"].tolist() + df_fahrten["Jahr"].tolist())))
jahr = st.selectbox("Jahr auswählen", jahre)

df_docs_jahr = df_docs[df_docs["Jahr"] == jahr]
df_fahrten_jahr = df_fahrten[df_fahrten["Jahr"] == jahr]

# ---------------------------------------------------
# KENNZAHLEN
# ---------------------------------------------------
st.subheader(f"📊 Kennzahlen für {jahr}")

sum_rechnungen = df_docs_jahr[df_docs_jahr["Typ"] == "rechnung"]["Summe"].sum()
sum_quittungen = df_docs_jahr[df_docs_jahr["Typ"] == "quittung"]["Summe"].sum()
sum_angebote = df_docs_jahr[df_docs_jahr["Typ"] == "angebot"]["Summe"].sum()
km_gesamt = df_fahrten_jahr["KM"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📑 Rechnungen", f"{sum_rechnungen:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col2:
    st.metric("🧾 Quittungen", f"{sum_quittungen:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("📃 Angebote", f"{sum_angebote:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

with col4:
    st.metric("🚗 Gefahrene Kilometer", f"{km_gesamt:.1f} km")

st.write("---")

# ---------------------------------------------------
# MONATSÜBERSICHT
# ---------------------------------------------------
st.subheader("📅 Monatsübersicht")

# Dokumente pro Monat
monate = [f"{i:02d}" for i in range(1, 13)]
df_monate = pd.DataFrame({"Monat": monate})

df_monate["Rechnungen (€)"] = df_monate["Monat"].apply(
    lambda m: df_docs_jahr[(df_docs_jahr["Monat"] == m) & (df_docs_jahr["Typ"] == "rechnung")]["Summe"].sum()
)

df_monate["Quittungen (€)"] = df_monate["Monat"].apply(
    lambda m: df_docs_jahr[(df_docs_jahr["Monat"] == m) & (df_docs_jahr["Typ"] == "quittung")]["Summe"].sum()
)

df_monate["Angebote (€)"] = df_monate["Monat"].apply(
    lambda m: df_docs_jahr[(df_docs_jahr["Monat"] == m) & (df_docs_jahr["Typ"] == "angebot")]["Summe"].sum()
)

df_monate["KM"] = df_monate["Monat"].apply(
    lambda m: df_fahrten_jahr[df_fahrten_jahr["Monat"] == m]["KM"].sum()
)

st.dataframe(df_monate, use_container_width=True)

st.write("---")

# ---------------------------------------------------
# EXPORT
# ---------------------------------------------------
st.subheader("📥 Export")

csv_data = df_monate.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Monatsübersicht als CSV herunterladen",
    data=csv_data,
    file_name=f"jahresbericht_{jahr}.csv",
    mime="text/csv"
)
