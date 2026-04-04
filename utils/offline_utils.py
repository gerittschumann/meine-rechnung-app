import os
from pathlib import Path
from utils.db import get_connection

# ---------------------------------------------------
# PFAD ZUM ARCHIV (Persistent Volume)
# ---------------------------------------------------
ARCHIV_DIR = Path("/mnt/data/archiv")


# ---------------------------------------------------
# ARCHIV-ORDNER SICHERSTELLEN
# ---------------------------------------------------
def ensure_archiv_folder() -> bool:
    """
    Stellt sicher, dass der Archiv-Ordner existiert.
    Wird beim Start der App ausgeführt.
    """
    try:
        ARCHIV_DIR.mkdir(parents=True, exist_ok=True)
        return ARCHIV_DIR.exists()
    except Exception:
        return False


# ---------------------------------------------------
# PDF PRÜFEN
# ---------------------------------------------------
def check_pdf_exists(nummer: str) -> bool:
    """
    Prüft, ob ein PDF mit der angegebenen Dokumentnummer existiert.
    """
    pdf_path = ARCHIV_DIR / f"{nummer}.pdf"
    return pdf_path.exists()


# ---------------------------------------------------
# PDF LADEN
# ---------------------------------------------------
def load_pdf(nummer: str):
    """
    Lädt ein PDF aus dem Archiv.
    Gibt None zurück, wenn es nicht existiert.
    """
    pdf_path = ARCHIV_DIR / f"{nummer}.pdf"

    if not pdf_path.exists():
        return None

    try:
        with open(pdf_path, "rb") as f:
            return f.read()
    except Exception:
        return None


# ---------------------------------------------------
# ALLE PDFs LISTEN
# ---------------------------------------------------
def list_all_pdfs():
    """
    Gibt eine Liste aller PDFs im Archiv zurück.
    """
    if not ARCHIV_DIR.exists():
        return []

    try:
        return sorted([f.name for f in ARCHIV_DIR.glob("*.pdf")])
    except Exception:
        return []


# ---------------------------------------------------
# DATENBANKPRÜFUNG
# ---------------------------------------------------
def check_database():
    """
    Prüft, ob die SQLite-Datenbank existiert und Tabellen vorhanden sind.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cur.fetchall()]

        required = {"kunden", "dokumente", "positionen", "einstellungen", "leistungen", "fahrtenbuch"}

        missing = required - set(tables)

        conn.close()

        return {
            "ok": len(missing) == 0,
            "missing": sorted(list(missing)),
            "tables": sorted(tables)
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "missing": [],
            "tables": []
        }


# ---------------------------------------------------
# OFFLINE STATUS
# ---------------------------------------------------
def offline_status():
    """
    Gibt eine kompakte Übersicht über den Offline-Status zurück:
    - Archiv-Ordner vorhanden?
    - Anzahl gespeicherter PDFs
    - Datenbank-Status
    """
    archiv_ok = ARCHIV_DIR.exists()
    pdfs = list_all_pdfs()
    db = check_database()

    return {
        "archiv_ok": archiv_ok,
        "pdf_count": len(pdfs),
        "database_ok": db.get("ok", False),
        "database_missing": db.get("missing", []),
        "database_tables": db.get("tables", [])
    }
