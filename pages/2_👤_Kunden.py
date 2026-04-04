import streamlit as st
from utils.db import get_connection

# ---------------------------------------------------
# KUNDEN ANLEGEN
# ---------------------------------------------------
def kunden_anlegen(name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor()

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
    cur = conn.cursor()

    cur.execute("SELECT * FROM kunden ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


# ---------------------------------------------------
# EINEN KUNDEN LADEN
# ---------------------------------------------------
def kunde_laden(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM kunden WHERE id = %s", (id,))
    row = cur.fetchone()

    conn.close()
    return row


# ---------------------------------------------------
# KUNDEN AKTUALISIEREN
# ---------------------------------------------------
def kunden_aktualisieren(id, name, adresse, plz, ort, email, telefon):
    conn = get_connection()
    cur = conn.cursor()

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
    cur = conn.cursor()

    cur.execute("DELETE FROM kunden WHERE id = %s", (id,))

    conn.commit()
    conn.close()
