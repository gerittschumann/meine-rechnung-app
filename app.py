import streamlit as st

st.set_page_config(
    page_title="Nebengewerbe App",
    page_icon="🚚",
    layout="wide"
)

st.title("🏠 Dashboard")
st.write("Willkommen in deiner Nebengewerbe-App!")

st.info("Nutze das Menü links, um Rechnungen, Angebote, Quittungen, Ausgaben, Fahrten und mehr zu verwalten.")

from utils.offline_utils import sync_pending

synced = sync_pending()
if synced > 0:
    st.success(f"{synced} offline gespeicherte Einträge wurden synchronisiert.")

