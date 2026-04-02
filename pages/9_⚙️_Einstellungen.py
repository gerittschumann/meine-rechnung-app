import streamlit as st
from utils.db import load_einstellungen, save_einstellungen

st.set_page_config(
    page_title="⚙️ Einstellungen",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Einstellungen – Firmendaten")

st.write("""
Hier kannst du deine Firmendaten hinterlegen.  
Diese Informationen werden automatisch in **Rechnungen**, **Angeboten** und **Quittungen** verwendet.
""")

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
daten = load_einstellungen()

if daten:
    firma_name = daten["firma_name"]
    firma_adresse = daten["firma_adresse"]
    firma_plz = daten["firma_plz"]
    firma_ort = daten["firma_ort"]
    steuernummer = daten["steuernummer"]
    iban = daten["iban"]
    bic = daten["bic"]
else:
    firma_name = ""
    firma_adresse = ""
    firma_plz = ""
    firma_ort = ""
    steuernummer = ""
    iban = ""
    bic = ""

# ---------------------------------------------------
# FORMULAR
# ---------------------------------------------------
with st.form("einstellungen_formular"):
    st.subheader("🏢 Firmendaten")

    firma_name = st.text_input("Firmenname", value=firma_name)
    firma_adresse = st.text_input("Adresse", value=firma_adresse)
    firma_plz = st.text_input("PLZ", value=firma_plz)
    firma_ort = st.text_input("Ort", value=firma_ort)

    st.subheader("💼 Steuer / Bank")

    steuernummer = st.text_input("Steuernummer", value=steuernummer)
    iban = st.text_input("IBAN", value=iban)
    bic = st.text_input("BIC", value=bic)

    submitted = st.form_submit_button("💾 Speichern")

    if submitted:
        save_einstellungen({
            "firma_name": firma_name,
            "firma_adresse": firma_adresse,
            "firma_plz": firma_plz,
            "firma_ort": firma_ort,
            "steuernummer": steuernummer,
            "iban": iban,
            "bic": bic
        })

        st.success("Einstellungen gespeichert.")
        st.experimental_rerun()
