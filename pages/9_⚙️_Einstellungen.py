import streamlit as st
from utils.db import load_einstellungen, save_einstellungen

st.title("⚙️ Einstellungen")

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
if st.button("💾 Einstellungen speichern"):
    data = {
        "firma_name": firma_name,
        "firma_adresse": firma_adresse,
        "firma_plz": firma_plz,
        "firma_ort": firma_ort,
        "inhaber_name": inhaber_name,
        "firma_email": firma_email,
        "steuernummer": steuernummer,
        "iban": iban,
        "bic": bic,
        "text_rechnung": text_rechnung,
        "text_angebot": text_angebot,
        "text_quittung": text_quittung
    }

    save_einstellungen(data)
    st.success("Einstellungen wurden gespeichert.")

# ---------------------------------------------------
# FIRMENDATEN
# ---------------------------------------------------
st.header("🏢 Firmendaten")

firma_name = st.text_input("Firmenname", value=einstellungen.get("firma_name", ""))
firma_adresse = st.text_input("Adresse", value=einstellungen.get("firma_adresse", ""))
firma_plz = st.text_input("PLZ", value=einstellungen.get("firma_plz", ""))
firma_ort = st.text_input("Ort", value=einstellungen.get("firma_ort", ""))

st.write("---")

# ---------------------------------------------------
# INHABER / KONTAKT
# ---------------------------------------------------
st.header("👤 Inhaber / Kontakt")

inhaber_name = st.text_input("Vor- und Nachname", value=einstellungen.get("inhaber_name", ""))
firma_email = st.text_input("E-Mail-Adresse", value=einstellungen.get("firma_email", ""))

st.write("---")

# ---------------------------------------------------
# STEUER / BANK
# ---------------------------------------------------
st.header("💼 Steuer- & Bankdaten")

steuernummer = st.text_input("Steuernummer", value=einstellungen.get("steuernummer", ""))
iban = st.text_input("IBAN", value=einstellungen.get("iban", ""))
bic = st.text_input("BIC", value=einstellungen.get("bic", ""))

st.write("---")

# ---------------------------------------------------
# STANDARD TEXTE
# ---------------------------------------------------
st.header("📝 Standardtexte")

text_rechnung = st.text_area("Text für Rechnungen", value=einstellungen.get("text_rechnung", ""))
text_angebot = st.text_area("Text für Angebote", value=einstellungen.get("text_angebot", ""))
text_quittung = st.text_area("Text für Quittungen", value=einstellungen.get("text_quittung", ""))

st.write("---")

# ---------------------------------------------------
# SPEICHERN
# ---------------------------------------------------
if st.button("💾 Einstellungen speichern"):
    data = {
        "firma_name": firma_name,
        "firma_adresse": firma_adresse,
        "inhaber_name": inhaber_name
        "firma_plz": firma_plz,
        "firma_ort": firma_ort,
        "firma_email": firma_email,
        "steuernummer": steuernummer,
        "iban": iban,
        "bic": bic,
        "text_rechnung": text_rechnung,
        "text_angebot": text_angebot,
        "text_quittung": text_quittung,
        
    }

    save_einstellungen(data)
    st.success("Einstellungen wurden gespeichert.")
