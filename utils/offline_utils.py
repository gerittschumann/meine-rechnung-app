import streamlit as st
from utils.supabase_utils import get_supabase

# ---------------------------------------------------
# Supabase Client erzeugen (erst wenn Streamlit läuft)
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# Offline gespeicherte Einträge synchronisieren
# ---------------------------------------------------
def sync_pending():
    # Falls keine Offline-Daten existieren → nichts tun
    if "offline_entries" not in st.session_state:
        return 0

    entries = st.session_state["offline_entries"]
    if not entries:
        return 0

    # Einträge hochladen
    for entry in entries:
        supabase.table("belege").insert(entry).execute()

    # Offline-Daten löschen
    st.session_state["offline_entries"] = []

    return len(entries)
