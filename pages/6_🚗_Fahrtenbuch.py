import streamlit as st
from utils.db import get_connection
import pandas as pd
import datetime

st.set_page_config(
    page_title="🚗 Fahrtenbuch",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Fahrtenbuch – Finanzamt-konform")

st.write("""
Hier kannst du deine Fahrten für das Finanzamt dokumentieren.

Erfasst werden:
- Datum
- Startadresse
- Zieladresse
- Zweck der Fahrt
- Gesamte Kilometer (manuell eingetragen)

Die KM-Pauschale wird später automatisch in der Steuererklärung berücksichtigt.
""")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# NEUE FAHRT HINZUFÜGEN
# ---------------------------------------------------
st.subheader("➕ Neue Fahrt eintragen")

with st.form("fahrt_form"):
    datum = st.date_input("Datum", datetime.date.today())
    start = st.text_input("Startadresse")
    ziel = st.text_input("Zieladresse")
    zweck = st.text_input("Zweck der Fahrt")
    km_gesamt = st.number_input("Gesamte Kilometer", min_value=0.1, step=0.1)

    submitted = st.form_submit_button("Speichern")

    if submitted:
        cur.execute("""
            INSERT INTO fahrtenbuch (datum, start, ziel, zweck, km_diff)
            VALUES (?, ?, ?, ?, ?)
        """, (datum.isoformat(), start, ziel, zweck, km_gesamt))
        conn.commit()
        st.success("Fahrt gespeichert.")
        st.experimental_rerun()

# ---------------------------------------------------
# FAHRTEN ANZEIGEN
# ---------------------------------------------------
st.subheader("📋 Bisherige Fahrten")

cur.execute("SELECT * FROM fahrtenbuch ORDER BY datum DESC")
fahrten = [dict(row) for row in cur.fetchall()]

if not fahrten:
    st.info("Noch keine Fahrten eingetragen.")
else:
    df = pd.DataFrame(fahrten)
    df.columns = ["ID", "Datum", "Start", "Ziel", "Zweck", "KM gesamt", "Erstellt am"]
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------
# FAHRT LÖSCHEN
# ---------------------------------------------------
st.subheader("🗑️ Fahrt löschen")

if fahrten:
    ids = [f["id"] for f in fahrten]
    delete_id = st.selectbox("Fahrt auswählen", ids)

    if st.button("Löschen"):
        cur.execute("DELETE FROM fahrtenbuch WHERE id = ?", (delete_id,))
        conn.commit()
        st.success("Fahrt gelöscht.")
        st.experimental_rerun()

conn.close()
