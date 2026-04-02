import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

    # Dokumente (Rechnung/Angebot/Quittung)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dokumente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT NOT NULL,              -- rechnung / angebot / quittung
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
