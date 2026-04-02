import streamlit as st
from utils.db import get_connection

st.set_page_config(
    page_title="🧍 Kunden",
    page_icon="🧍",
    layout="wide"
)

st.title("🧍 Kundenverwaltung")

# ---------------------------------------------------
# FUNKTIONEN
# ---------------------------------------------------

def lade_kunden():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM kunden ORDER BY name ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def kunden_anlegen(name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO kunden (name, adresse, plz, ort, email, telefon)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, adresse, plz, ort, email, telefon))
    conn.commit()
    conn.close()

def kunden_aktualisieren(kunden_id, name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE kunden SET
            name = ?,
            adresse = ?,
            plz = ?,
            ort = ?,
            email = ?,
            telefon = ?
        WHERE id = ?
    """, (name, adresse, plz, ort, email, telefon, kunden_id))
    conn.commit()
    conn.close()

def kunden_loeschen(kunden_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM kunden WHERE id = ?", (kunden_id,))
    conn.commit()
    conn.close()

# ---------------------------------------------------
# KUNDENLISTE
# ---------------------------------------------------

st.subheader("📋 Kundenliste")

kunden = lade_kunden()

if not kunden:
    st.info("Noch keine Kunden vorhanden.")
else:
    for k in kunden:
        with st.expander(f"{k['name']} (ID: {k['id']})"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Adresse:** {k['adresse']}")
                st.write(f"**PLZ / Ort:** {k['plz']} {k['ort']}")
                st.write(f"**E-Mail:** {k['email']}")
                st.write(f"**Telefon:** {k['telefon']}")

            with col2:
                if st.button("Bearbeiten", key=f"edit_{k['id']}"):
                    st.session_state["edit_kunde"] = k

                if st.button("Löschen", key=f"delete_{k['id']}"):
                    kunden_loeschen(k['id'])
                    st.success("Kunde gelöscht.")
                    st.experimental_rerun()

st.write("---")

# ---------------------------------------------------
# KUNDEN BEARBEITEN
# ---------------------------------------------------

if "edit_kunde" in st.session_state:
    k = st.session_state["edit_kunde"]

    st.subheader(f"✏️ Kunde bearbeiten: {k['name']}")

    name = st.text_input("Name", k["name"])
    adresse = st.text_input("Adresse", k["adresse"])
    plz = st.text_input("PLZ", k["plz"])
    ort = st.text_input("Ort", k["ort"])
    email = st.text_input("E-Mail", k["email"])
    telefon = st.text_input("Telefon", k["telefon"])

    if st.button("Änderungen speichern"):
        kunden_aktualisieren(k["id"], name, adresse, plz, ort, email, telefon)
        st.success("Kunde aktualisiert.")
        del st.session_state["edit_kunde"]
        st.experimental_rerun()

    st.write("---")

# ---------------------------------------------------
# NEUEN KUNDEN ANLEGEN
# ---------------------------------------------------

st.subheader("➕ Neuen Kunden anlegen")

with st.form("kunden_formular"):
    name = st.text_input("Name")
    adresse = st.text_input("Adresse")
    plz = st.text_input("PLZ")
    ort = st.text_input("Ort")
    email = st.text_input("E-Mail")
    telefon = st.text_input("Telefon")

    submitted = st.form_submit_button("Kunde speichern")

    if submitted:
        if name.strip() == "":
            st.error("Name darf nicht leer sein.")
        else:
            kunden_anlegen(name, adresse, plz, ort, email, telefon)
            st.success("Kunde erfolgreich angelegt.")
            st.experimental_rerun()
