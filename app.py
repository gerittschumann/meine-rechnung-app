import streamlit as st

# Supabase-Funktionen importieren
from utils.supabase_utils import (
    get_supabase,
    get_belege_df,
    get_positionen_df,
    upload_pdf_to_supabase
)

# Offline-Sync importieren
from utils.offline_utils import sync_pending

# ---------------------------------------------------
# Supabase Client erzeugen (JETZT ist Streamlit bereit)
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.set_page_config(
    page_title="Nebengewerbe App",
    page_icon="🚚",
    layout="wide"
)

st.title("🏠 Dashboard")
st.write("Willkommen in deiner Nebengewerbe-App!")

st.info("Nutze das Menü links, um Rechnungen, Angebote, Quittungen, Ausgaben, Fahrten und mehr zu verwalten.")

# ---------------------------------------------------
# Offline gespeicherte Einträge synchronisieren
# ---------------------------------------------------
synced = sync_pending()
if synced > 0:
    st.success(f"{synced} offline gespeicherte Einträge wurden synchronisiert.")

# ---------------------------------------------------
# Beispiel: Belege laden (optional)
# ---------------------------------------------------
# df_belege = get_belege_df(supabase)
# st.write(df_belege)

# ---------------------------------------------------
# Beispiel: Positionen laden (optional)
# ---------------------------------------------------
# df_positionen = get_positionen_df(supabase)
# st.write(df_positionen)
