import streamlit as st

# ---------------------------------------------------
# Page Config – MUSS GANZ OBEN STEHEN
# ---------------------------------------------------
st.set_page_config(
    page_title="Kunden",
    page_icon="👤",
    layout="wide"
)

# ---------------------------------------------------
# Supabase-Funktionen importieren
# ---------------------------------------------------
from utils.supabase_utils import (
    get_supabase,
    get_belege_df,
    get_positionen_df,
    upload_pdf_to_supabase
)

# ---------------------------------------------------
# Supabase Client erzeugen
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("👤 Kundenverwaltung")
st.write("Hier kannst du deine Kunden verwalten.")

# ---------------------------------------------------
# Beispiel: Kunden laden (falls du eine Tabelle hast)
# ---------------------------------------------------
try:
    df = supabase.table("kunden").select("*").execute().data
    if not df:
        st.info("Noch keine Kunden vorhanden.")
    else:
        st.dataframe(df)
except Exception as e:
    st.error(f"Fehler beim Laden der Kunden: {e}")
