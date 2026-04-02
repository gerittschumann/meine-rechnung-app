from supabase import create_client
import os
import pandas as pd

# ---------------------------------------------------
# Supabase Client
# ---------------------------------------------------
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Supabase URL oder KEY fehlen in den Umgebungsvariablen.")

    return create_client(url, key)


# ---------------------------------------------------
# Belege laden (für Dashboard)
# ---------------------------------------------------
def get_belege_df(supabase):
    """
    Lädt alle Dokumente (Rechnungen, Angebote, Quittungen)
    und gibt sie als DataFrame zurück.
    """

    try:
        data = supabase.table("dokumente").select("*").order("erstellt_am", desc=True).execute().data
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Datum in echtes Datum umwandeln
        if "erstellt_am" in df.columns:
            df["erstellt_am"] = pd.to_datetime(df["erstellt_am"], errors="coerce")

        return df

    except Exception as e:
        print("Fehler in get_belege_df:", e)
        return pd.DataFrame()
