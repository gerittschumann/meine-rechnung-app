from utils.supabase_utils import get_supabase

# Supabase Client erzeugen
supabase = get_supabase()

# ---------------------------------------------------
# Beispiel-Funktion: Dokument erstellen
# ---------------------------------------------------
def create_document(data):
    """
    Erzeugt ein PDF-Dokument oder speichert Daten in Supabase.
    Passe diese Funktion nach Bedarf an.
    """
    # Beispiel: Daten in Supabase speichern
    try:
        result = supabase.table("dokumente").insert(data).execute()
        return result
    except Exception as e:
        return {"error": str(e)}
