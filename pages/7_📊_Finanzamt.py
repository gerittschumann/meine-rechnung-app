import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="🏦 Finanzamt",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Auswertung für das Finanzamt / Steuerberater")

st.write("""
Hier findest du eine komprimierte Übersicht deiner relevanten Daten für das Finanzamt:
- Umsätze aus Rechnungen
- Einnahmen aus Quittungen
- Angebote (unverbindlich)
- Fahrtenbuch-Kilometer
- Export als CSV
""")

conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# UMSÄTZE / EINNAHMEN
# ---------------------------------------------------
cur.execute("""
    SELECT 
        strftime('%Y', erstellt_am) AS jahr,
        SUM(CASE WHEN typ = 'rechnung' THEN summe ELSE 0 END) AS rechnungen,
        SUM(CASE WHEN typ = 'quittung' THEN summe ELSE 0 END) AS quittungen,
        SUM(CASE WHEN typ = 'angebot' THEN summe ELSE 0 END) AS angebote
    FROM dokumente
    GROUP BY jahr
    ORDER BY jahr DESC
""")
umsatz_jahre = cur.fetchall()

# ---------------------------------------------------
# FAHRTENBUCH
# ---------------------------------------------------
cur.execute("""
    SELECT 
        strftime('%Y', datum) AS jahr,
        SUM(km_diff) AS km_gesamt
    FROM fahrtenbuch
    GROUP BY jahr
    ORDER BY jahr DESC
""")
fahrten_jahre = cur.fetchall()

# ---------------------------------------------------
# DETAIL-DOKUMENTE FÜR EXPORT
# ---------------------------------------------------
cur.execute("""
    SELECT 
        typ,
        nummer,
        kunde_id,
        summe,
        erstellt_am
    FROM dokumente
    ORDER BY erstellt_am DESC
""")
dokumente = cur.fetchall()

conn.close()

# ---------------------------------------------------
# JAHRESÜBERSICHT UMSÄTZE
# ---------------------------------------------------
st.subheader("📅 Jahresübersicht – Umsätze & Einnahmen")

if not umsatz_jahre:
    st.info("Noch keine Dokumente vorhanden.")
else:
    df_umsatz = pd.DataFrame(umsatz_jahre)
    df_umsatz.columns = ["Jahr", "Rechnungen (€)", "Quittungen (€)", "Angebote (€)"]
    st.dataframe(df_umsatz, use_container_width=True)

# ---------------------------------------------------
# JAHRESÜBERSICHT FAHRTEN
# ---------------------------------------------------
st.subheader("🚗 Jahresübersicht – Fahrtenbuch (Kilometer)")

if not fahrten_jahre:
    st.info("Noch keine Fahrten im Fahrtenbuch.")
else:
    df_fahrten = pd.DataFrame(fahrten_jahre)
    df_fahrten.columns = ["Jahr", "Gefahrene Kilometer"]
    st.dataframe(df_fahrten, use_container_width=True)

# ---------------------------------------------------
# DETAIL-EXPORT FÜR STEUERBERATER
# ---------------------------------------------------
st.subheader("📄 Detaildaten – Export für Steuerberater / Finanzamt")

if not dokumente:
    st.info("Noch keine Dokumente vorhanden.")
else:
    df_docs = pd.DataFrame(dokumente)
    df_docs.columns = ["Typ", "Nummer", "Kunden-ID", "Summe (€)", "Erstellt am"]

    st.dataframe(df_docs, use_container_width=True)

    csv_data = df_docs.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 CSV-Export (Dokumente)",
        data=csv_data,
        file_name="dokumente_fuer_steuerberater.csv",
        mime="text/csv"
    )
