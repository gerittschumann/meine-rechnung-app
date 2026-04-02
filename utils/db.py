import sqlite3
from pathlib import Path
import datetime

DB_PATH = Path("database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ---------------------------------------------------
    # KUNDEN
    # ---------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kunden (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            adresse TEXT,
            plz TEXT,
            ort TEXT,
            email TEXT,
            telefon TEXT,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------------------------------
    # EINSTELLUNGEN
    # ---------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS einstellungen (
            id INTEGER PRIMARY KEY,
            firma_name TEXT,
            firma_adresse TEXT,
            firma_plz TEXT,
            firma_ort TEXT,
            steuernummer TEXT,
            iban TEXT,
            bic TEXT
        )
    """)

    # ---------------------------------------------------
    # DOKUMENTE
    # ---------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dokumente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ TEXT,
            nummer TEXT,
            kunde_id INTEGER,
            pdf_path TEXT,
            summe REAL,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------------------------------
    # POSITIONEN (Dokument-Positionen)
    # ---------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positionen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dokument_id INTEGER,
            beschreibung TEXT,
            menge REAL,
            preis REAL,
            gesamt REAL
        )
    """)

    # ---------------------------------------------------
    # FAHRTENBUCH
    # ---------------------------------------------------
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

    # ---------------------------------------------------
    # LEISTUNGSKATALOG
    # ---------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leistungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            preis REAL,
            einheit TEXT,
            beschreibung TEXT,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# EINSTELLUNGEN LADEN / SPEICHERN
# ---------------------------------------------------

def load_einstellungen():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM einstellungen WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row


def save_einstellungen(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM einstellungen WHERE id = 1")

    cur.execute("""
        INSERT INTO einstellungen (
            id, firma_name, firma_adresse, firma_plz, firma_ort,
            steuernummer, iban, bic
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("firma_name", ""),
        data.get("firma_adresse", ""),
        data.get("firma_plz", ""),
        data.get("firma_ort", ""),
        data.get("steuernummer", ""),
        data.get("iban", ""),
        data.get("bic", "")
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------
# DOKUMENTNUMMERN GENERIEREN
# ---------------------------------------------------

def generate_next_number(typ: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT nummer FROM dokumente
        WHERE typ = ?
        ORDER BY id DESC LIMIT 1
    """, (typ,))

    last = cur.fetchone()

    if last:
        try:
            num = int(last["nummer"].split("-")[-1])
            next_num = num + 1
        except:
            next_num = 1
    else:
        next_num = 1

    year = datetime.datetime.now().year
    nummer = f"{typ[:2].upper()}-{year}-{next_num:04d}"

    conn.close()
    return nummer
