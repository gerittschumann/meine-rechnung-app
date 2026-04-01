import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    # Secrets laden
    url = st.secrets.get("SUPABASE_URL", None)
    key = st.secrets.get("SUPABASE_KEY", None)

    # DEBUG-AUSGABE
    st.write("DEBUG: SUPABASE_URL =", url)
    st.write("DEBUG: SUPABASE_KEY (Anfang) =", key[:10] + "..." if key else None)

    # Fehlerbehandlung
    if not url or not isinstance(url, str) or not url.startswith("https://"):
        st.error("Supabase URL ist ungültig oder fehlt.")
        raise ValueError("Supabase URL fehlt oder ist ungültig.")

    if not key or not isinstance(key, str):
        st.error("Supabase KEY ist ungültig oder fehlt.")
        raise ValueError("Supabase KEY fehlt oder ist ungültig.")

    # Supabase Client erzeugen
    return create_client(url, key)
