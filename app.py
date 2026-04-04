import streamlit as st
from streamlit_option_menu import option_menu

# Seiten laden
import pages.Übersicht as Übersicht
import pages.Kunden as Kunden
import pages.Rechnungen as Rechnungen
import pages.Einstellungen as Einstellungen

# Streamlit Layout
st.set_page_config(
    page_title="Meine Rechnung App",
    page_icon="📄",
    layout="wide"
)

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Übersicht", "Kunden", "Rechnungen", "Einstellungen"],
        icons=["house", "person", "file-text", "gear"],
        menu_icon="cast",
        default_index=0
    )

# Seitenlogik
if selected == "Übersicht":
    Übersicht.show()

elif selected == "Kunden":
    Kunden.show()

elif selected == "Rechnungen":
    Rechnungen.show()

elif selected == "Einstellungen":
    Einstellungen.show()
