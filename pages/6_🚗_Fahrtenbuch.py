import streamlit as st
from utils.db import get_connection
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="🚛 Fahrtenbuch",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Fahrtenbuch")

# ---------------------------------------------------
# DATENBANK: TABELLE ANLEGEN (falls nicht vorhanden)
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS fahrtenbuch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TEXT,
    start TEXT,
    ziel TEXT,
    zweck TEXT,
    km_start REAL,
    km_ende REAL,
    km_diff REAL,
    erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

# ---------------------------------------------------
# FUNKTIONEN
# ---------------------------------------------------

def lade_fahrten():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fahrtenbuch ORDER BY datum DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fahrt_anlegen(datum, start, ziel, zweck, km_start, km_ende):
    km_diff = km_ende - km_start
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fahrtenbuch (datum, start, ziel, zweck, km_start, km_ende, km_diff)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datum, start, ziel, zweck, km_start, km_ende, km_diff))
    conn.commit()
    conn.close()

def fahrt_loeschen(fahrt_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM fahrtenbuch WHERE id = ?", (fahrt_id,))
    conn.commit()
    conn.close()

# ---------------------------------------------------
# FAHRTEN ANZEIGEN
# ---------------------------------------------------

st.subheader("📋 Übersicht aller Fahrten")

fahrten = lade_fahrten()

if not fahrten:
    st.info("Noch keine Fahrten eingetragen.")
else:
    df = pd.DataFrame(fahrten)
    df.columns = ["ID", "Datum", "Start", "Ziel", "Zweck", "KM Start", "KM Ende", "KM Diff", "Erstellt am"]

    # Filter
    col1, col2 = st.columns(2)
    with col1:
        jahr_filter = st.selectbox("Jahr filtern", ["Alle"] + sorted(list({d["Datum"][:4] for d in fahrten})))
    with col2:
        monat_filter = st.selectbox("Monat filtern", ["Alle"] + [f"{i:02d}" for i in range(1, 13)])

    df_filtered = df.copy()

    if jahr_filter != "Alle":
        df_filtered = df_filtered[df_filtered["Datum"].str.startswith(jahr_filter)]

    if monat_filter != "Alle":
        df_filtered = df_filtered[df_filtered["Datum"].str[5:7] == monat_filter]

    st.dataframe(df_filtered, use_container_width=True)

    # Gesamtkilometer
    total_km = df_filtered["KM Diff"].sum()
    st.metric("🚗 Gefahrene Kilometer (gefiltert)", f"{total_km:.1f} km")

    # Löschfunktion
    st.write("---")
    st.subheader("🗑️ Fahrt löschen")
    fahrt_ids = df_filtered["ID"].tolist()
    if fahrt_ids:
        fahrt_id = st.selectbox("Fahrt-ID auswählen", fahrt_ids)
        if st.button("Fahrt löschen"):
            fahrt_loeschen(fahrt_id)
            st.success("Fahrt gelöscht.")
            st.experimental_rerun()

st.write("---")

# ---------------------------------------------------
# NEUE FAHRT ANLEGEN
# ---------------------------------------------------

st.subheader("➕ Neue Fahrt eintragen")

with st.form("fahrt_formular"):
    datum = st.date_input("Datum", datetime.today())
    start = st.text_input("Startadresse")
    ziel = st.text_input("Zieladresse")
    zweck = st.text_input("Zweck der Fahrt")
    km_start = st.number_input("KM-Stand Start", min_value=0.0, step=0.1)
    km_ende = st.number_input("KM-Stand Ende", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Fahrt speichern")

    if submitted:
        if km_ende < km_start:
            st.error("KM-Stand Ende darf nicht kleiner sein als Start.")
        else:
            fahrt_anlegen(str(datum), start, ziel, zweck, km_start, km_ende)
            st.success("Fahrt erfolgreich eingetragen.")
            st.experimental_rerun()
