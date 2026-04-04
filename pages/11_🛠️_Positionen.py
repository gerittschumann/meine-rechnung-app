import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="📈 Leistungskatalog",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Leistungskatalog – Eigene Leistungen verwalten")

st.write("""
Hier kannst du deine eigenen Leistungen speichern, z. B.:

- Grundgebühr
- Anfahrt
- Arbeitsstunde
- Pauschalen
- Materialpreise

Diese Leistungen kannst du später in Rechnungen, Angeboten und Quittungen auswählen.
""")

# ---------------------------------------------------
# DATEN LADEN
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT * FROM leistungen ORDER BY name ASC")
leistungen = [dict(row) for row in cur.fetchall()]

# ---------------------------------------------------
# LEISTUNGEN ANZEIGEN
# ---------------------------------------------------
st.subheader("📋 Gespeicherte Leistungen")

if not leistungen:
    st.info("Noch keine Leistungen gespeichert.")
else:
    df = pd.DataFrame(leistungen)
    df.columns = ["ID", "Name", "Preis (€)", "Einheit", "Beschreibung", "Erstellt am"]
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------
# LEISTUNG LÖSCHEN
# ---------------------------------------------------
st.write("---")
st.subheader("🗑️ Leistung löschen")

if leistungen:
    ids = [l["id"] for l in leistungen]
    delete_id = st.selectbox("Leistung auswählen", ids)

    if st.button("Löschen"):
        cur.execute("DELETE FROM leistungen WHERE id = ?", (delete_id,))
        conn.commit()
        st.success("Leistung gelöscht.")
        st.experimental_rerun()

# ---------------------------------------------------
# NEUE LEISTUNG ANLEGEN
# ---------------------------------------------------
st.write("---")
st.subheader("➕ Neue Leistung hinzufügen")

with st.form("leistung_form"):
    name = st.text_input("Name der Leistung")
    preis = st.number_input("Preis (€)", min_value=0.0, step=0.5)
    einheit = st.text_input("Einheit (z. B. Stunde, Stück, Pauschale)")
    beschreibung = st.text_area("Beschreibung (optional)")

    submitted = st.form_submit_button("Speichern")

    if submitted:
        if name.strip() == "":
            st.error("Der Name darf nicht leer sein.")
        else:
            cur.execute("""
                INSERT INTO leistungen (name, preis, einheit, beschreibung)
                VALUES (?, ?, ?, ?)
            """, (name, preis, einheit, beschreibung))

            conn.commit()
            st.success("Leistung gespeichert.")
            st.experimental_rerun()

conn.close()
