import streamlit as st
import psycopg2.extras
from utils.db import get_connection

# ---------------------------------------------------
# KUNDEN ANLEGEN
# ---------------------------------------------------
def kunden_anlegen(name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        INSERT INTO kunden (name, adresse, plz, ort, email, telefon)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, adresse, plz, ort, email, telefon))

    conn.commit()
    conn.close()


# ---------------------------------------------------
# ALLE KUNDEN LADEN
# ---------------------------------------------------
def kunden_laden():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM kunden ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


# ---------------------------------------------------
# EINEN KUNDEN LADEN
# ---------------------------------------------------
def kunde_laden(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM kunden WHERE id = %s", (id,))
    row = cur.fetchone()

    conn.close()
    return row


# ---------------------------------------------------
# KUNDEN AKTUALISIEREN
# ---------------------------------------------------
def kunden_aktualisieren(id, name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        UPDATE kunden
        SET name = %s,
            adresse = %s,
            plz = %s,
            ort = %s,
            email = %s,
            telefon = %s
        WHERE id = %s
    """, (name, adresse, plz, ort, email, telefon, id))

    conn.commit()
    conn.close()


# ---------------------------------------------------
# KUNDEN LÖSCHEN
# ---------------------------------------------------
def kunden_loeschen(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("DELETE FROM kunden WHERE id = %s", (id,))

    conn.commit()
    conn.close()


# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------

st.title("Kunden")

# Formular zum Anlegen eines neuen Kunden
with st.form("kunden_formular"):
    name = st.text_input("Name")
    adresse = st.text_input("Adresse")
    plz = st.text_input("PLZ")
    ort = st.text_input("Ort")
    email = st.text_input("E-Mail")
    telefon = st.text_input("Telefon")

    submitted = st.form_submit_button("Kunde anlegen")

    if submitted:
        kunden_anlegen(name, adresse, plz, ort, email, telefon)
        st.success("Kunde wurde angelegt.")
        st.experimental_rerun()

# Kundenliste anzeigen
st.subheader("Alle Kunden")

kunden = kunden_laden()

if kunden:
    for k in kunden:
        st.write(
            f"{k.get('id', '')} – "
            f"{k.get('name', '')} – "
            f"{k.get('adresse', '')} – "
            f"{k.get('plz', '')} – "
            f"{k.get('ort', '')} – "
            f"{k.get('email', '')} – "
            f"{k.get('telefon', '')}"
        )
else:
    st.info("Noch keine Kunden vorhanden.")
