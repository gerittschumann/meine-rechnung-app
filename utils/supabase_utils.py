import streamlit as st
from supabase import create_client, Client
import pandas as pd

# ---------------------------------------------------
# Supabase Client erzeugen
# ---------------------------------------------------
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# ---------------------------------------------------
# Belege aus der Datenbank laden
# ---------------------------------------------------
def get_belege_df(supabase: Client) -> pd.DataFrame:
    response = supabase.table("belege").select("*").execute()
    data = response.data or []
    return pd.DataFrame(data)

# ---------------------------------------------------
# Positionen aus der Datenbank laden
# ---------------------------------------------------
def get_positionen_df(supabase: Client) -> pd.DataFrame:
    response = supabase.table("positionen").select("*").execute()
    data = response.data or []
    return pd.DataFrame(data)
