import psycopg2
import psycopg2.extras
import os

# ---------------------------------------------------
# DATENBANKVERBINDUNG (GLOBALER DICTCURSOR FIX)
# ---------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
def load_einstellungen():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM einstellungen LIMIT 1")
    row = cur.fetchone()

    conn.close()
    return row


# ---------------------------------------------------
# EINSTELLUNGEN SPEICHERN
# ---------------------------------------------------
def save_einstellungen(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE einstellungen SET
            firma_name = %s,
            firma_adresse = %s,
            firma_plz = %s,
            firma_ort = %s,
            firma_email = %s,
            inhaber_name = %s,
            steuernummer = %s,
            iban = %s,
            bic = %s
        WHERE id = 1
    """, (
        data.get("firma_name"),
        data.get("firma_adresse"),
        data.get("firma_plz"),
        data.get("firma_ort"),
        data.get("firma_email"),
        data.get("inhaber_name"),
        data.get("steuernummer"),
        data.get("iban"),
        data.get("bic")
    ))

    conn.commit()
    conn.close()
