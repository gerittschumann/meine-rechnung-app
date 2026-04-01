import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64

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

# ---------------------------------------------------
# PDF in Supabase Storage hochladen
# ---------------------------------------------------
def upload_pdf_to_supabase(supabase: Client, file_bytes: bytes, filename: str) -> str:
    """
    Lädt ein PDF in den Supabase Storage Bucket 'pdfs' hoch.
    Gibt die öffentliche URL zurück.
    """

    # Datei hochladen
    supabase.storage.from_("pdfs").upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )

    # Öffentliche URL erzeugen
    public_url = supabase.storage.from_("pdfs").get_public_url(filename)
    return public_url
