import streamlit as st
from supabase import create_client
import pandas as pd

# Supabase Client laden
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# -----------------------------
# BELEGE LADEN
# -----------------------------
def get_belege_df():
    data = supabase.table("belege").select("*").order("datum").execute().data
    df = pd.DataFrame(data)

    for col in ["typ", "stunden", "pdf_url"]:
        if col not in df.columns:
            df[col] = None

    return df

# -----------------------------
# POSITIONEN LADEN
# -----------------------------
def get_positionen_df():
    data = supabase.table("positionen").select("*").execute().data
    df = pd.DataFrame(data)

    for col in ["leistung", "menge", "preis", "gesamt"]:
        if col not in df.columns:
            df[col] = None

    return df

# -----------------------------
# PDF HOCHLADEN
# -----------------------------
def upload_pdf_to_supabase(pdf_bytes, filename):
    path = f"pdfs/{filename}"
    supabase.storage.from_("pdfs").upload(path, pdf_bytes, {"content-type": "application/pdf"})
    url = supabase.storage.from_("pdfs").get_public_url(path)
    return url
