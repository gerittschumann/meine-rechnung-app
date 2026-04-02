import streamlit as st

# ---------------------------------------------------
# Page Config – MUSS GANZ OBEN STEHEN
# ---------------------------------------------------
st.set_page_config(
    page_title="Rechnungen & Angebote",
    page_icon="📄",
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
st.title("📄 Rechnungen & Angebote")
st.write("Hier kannst du Rechnungen und Angebote verwalten.")

# Tabs für Übersicht
tab1, tab2 = st.tabs(["📄 Rechnungen", "📝 Angebote"])

# ---------------------------------------------------
# TAB: Rechnungen
# ---------------------------------------------------
with tab1:
    st.subheader("📄 Rechnungen")

    try:
        data = supabase.table("rechnungen").select("*").execute().data

        if not data:
            st.info("Noch keine Rechnungen vorhanden.")
        else:
            st.dataframe(data)

    except Exception as e:
        st.error(f"Fehler beim Laden der Rechnungen: {e}")

# ---------------------------------------------------
# TAB: Angebote
# ---------------------------------------------------
with tab2:
    st.subheader("📝 Angebote")

    try:
        data = supabase.table("angebote").select("*").execute().data

        if not data:
            st.info("Noch keine Angebote vorhanden.")
        else:
            st.dataframe(data)

    except Exception as e:
        st.error(f"Fehler beim Laden der Angebote: {e}")
