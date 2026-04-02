import sqlite3
from pathlib import Path
import datetime
import os

# ---------------------------------------------------
# PFAD ZUR SQLITE-DATENBANK
# ---------------------------------------------------
# Lokal: database.db im Projektordner
# Railway: ebenfalls database.db (wird im Container gespeichert)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"

# ---------------------------------------------------
# VERBINDUNG HERSTELLEN
# ---------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------
# DATENBANK INITIALISIEREN
# ---------------------------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Kunden
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kunden (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        adresse TEXT,
        plz TEXT,
        ort TEXT,
        email TEXT,
        telefon TEXT
    )
    """)

    # Dokumente (Rechnung, Angebot, Quittung)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dokumente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT NOT NULL,
        nummer TEXT NOT NULL,
        kunde_id INTEGER,
        pdf_path TEXT,
        summe REAL,
        erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Positionen
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

    # Einstellungen
    cur.execute("""
    CREATE TABLE IF NOT EXISTS einstellungen (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        firma_name TEXT,
        firma_adresse TEXT,
        firma_plz TEXT,
        firma_ort TEXT,
        steuernummer TEXT,
        iban TEXT,
        bic TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------------------------------
# RECHNUNGSNUMMER GENERIEREN
# ---------------------------------------------------
def generate_next_number(dokument_typ: str) -> str:
    jahr = datetime.datetime.now().year
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT nummer FROM dokumente
        WHERE typ = ?
        AND nummer LIKE ?
        ORDER BY id DESC
        LIMIT 1
    """, (dokument_typ, f"%-{jahr}-%"))

    row = cur.fetchone()
    if row:
        letzte = row["nummer"]  # z.B. RE-2026-0007
        laufend = int(letzte.split("-")[2]) + 1
    else:
        laufend = 1

    prefix = dokument_typ.upper()[0:2]  # rechnung -> RE, angebot -> AN
    conn.close()
    return f"{prefix}-{jahr}-{laufend:04d}"

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
def load_einstellungen():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM einstellungen WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row

# ---------------------------------------------------
# EINSTELLUNGEN SPEICHERN
# ---------------------------------------------------
def save_einstellungen(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM einstellungen WHERE id = 1")
    exists = cur.fetchone()

    if exists:
        cur.execute("""
            UPDATE einstellungen SET
                firma_name = ?,
                firma_adresse = ?,
                firma_plz = ?,
                firma_ort = ?,
                steuernummer = ?,
                iban = ?,
                bic = ?
            WHERE id = 1
        """, (
            data["firma_name"],
            data["firma_adresse"],
            data["firma_plz"],
            data["firma_ort"],
            data["steuernummer"],
            data["iban"],
            data["bic"]
        ))
    else:
        cur.execute("""
            INSERT INTO einstellungen (
                id, firma_name, firma_adresse, firma_plz, firma_ort,
                steuernummer, iban, bic
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["firma_name"],
            data["firma_adresse"],
            data["firma_plz"],
            data["firma_ort"],
            data["steuernummer"],
            data["iban"],
            data["bic"]
        ))

    conn.commit()
    conn.close()
