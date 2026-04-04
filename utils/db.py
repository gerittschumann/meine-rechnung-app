import os
import datetime
import psycopg2
import psycopg2.extras

# ---------------------------------------------------
# VERBINDUNG HERSTELLEN (NEON POSTGRES)
# ---------------------------------------------------
NEON_DB_URL = os.getenv("NEON_DB_URL")


def get_connection():
    if not NEON_DB_URL:
        raise RuntimeError("NEON_DB_URL ist nicht gesetzt (Render Environment Variable prüfen).")
    conn = psycopg2.connect(NEON_DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


# ---------------------------------------------------
# DATENBANK INITIALISIEREN
# ---------------------------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # KUNDEN
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kunden (
            id SERIAL PRIMARY KEY,
            name TEXT,
            adresse TEXT,
            plz TEXT,
            ort TEXT,
            email TEXT,
            telefon TEXT,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # EINSTELLUNGEN
    cur.execute("""
        CREATE TABLE IF NOT EXISTS einstellungen (
            id INTEGER PRIMARY KEY,
            firma_name TEXT,
            inhaber_name TEXT,
            firma_adresse TEXT,
            firma_plz TEXT,
            firma_ort TEXT,
            firma_email TEXT,
            steuernummer TEXT,
            iban TEXT,
            bic TEXT,
            text_rechnung TEXT,
            text_angebot TEXT,
            text_quittung TEXT
        )
    """)

    # DOKUMENTE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dokumente (
            id SERIAL PRIMARY KEY,
            typ TEXT,
            nummer TEXT,
            kunde_id INTEGER,
            pdf_path TEXT,
            summe REAL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # POSITIONEN
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positionen (
            id SERIAL PRIMARY KEY,
            dokument_id INTEGER,
            beschreibung TEXT,
            menge REAL,
            preis REAL,
            gesamt REAL
        )
    """)

    # FAHRTENBUCH
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fahrtenbuch (
            id SERIAL PRIMARY KEY,
            datum TEXT,
            start TEXT,
            ziel TEXT,
            zweck TEXT,
            km_start REAL,
            km_ende REAL,
            km_diff REAL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # LEISTUNGSKATALOG
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leistungen (
            id SERIAL PRIMARY KEY,
            name TEXT,
            preis REAL,
            einheit TEXT,
            beschreibung TEXT,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    return dict(row) if row else None


def save_einstellungen(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM einstellungen WHERE id = 1")

    cur.execute("""
        INSERT INTO einstellungen (
            id, firma_name, inhaber_name, firma_adresse, firma_plz, firma_ort,
            firma_email, steuernummer, iban, bic,
            text_rechnung, text_angebot, text_quittung
        )
        VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("firma_name", ""),
        data.get("inhaber_name", ""),
        data.get("firma_adresse", ""),
        data.get("firma_plz", ""),
        data.get("firma_ort", ""),
        data.get("firma_email", ""),
        data.get("steuernummer", ""),
        data.get("iban", ""),
        data.get("bic", ""),
        data.get("text_rechnung", ""),
        data.get("text_angebot", ""),
        data.get("text_quittung", "")
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
        WHERE typ = %s
        ORDER BY id DESC LIMIT 1
    """, (typ,))

    last = cur.fetchone()

    if last and last.get("nummer"):
        try:
            num = int(last["nummer"].split("-")[-1])
            next_num = num + 1
        except Exception:
            next_num = 1
    else:
        next_num = 1

    year = datetime.datetime.now().year
    nummer = f"{typ[:2].upper()}-{year}-{next_num:04d}"

    conn.close()
    return nummer
