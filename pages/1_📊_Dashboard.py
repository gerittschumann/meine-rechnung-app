import streamlit as st

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# Supabase-Funktionen importieren
# ---------------------------------------------------
from utils.supabase_utils import get_supabase, get_belege_df

# ---------------------------------------------------
# Supabase Client erzeugen
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("📊 Dashboard")
st.write("Übersicht deiner Belege und Daten")

# ---------------------------------------------------
# Belege laden
# ---------------------------------------------------
df = get_belege_df(supabase)

if df.empty:
    st.info("Noch keine Belege vorhanden.")
else:
    st.dataframe(df)
