import streamlit as st

# ---------------------------------------------------
# Page Config – MUSS GANZ OBEN STEHEN
# ---------------------------------------------------
st.set_page_config(
    page_title="Kunden",
    page_icon="👤",
    layout="wide"
)

# ---------------------------------------------------
# Supabase-Funktionen importieren
# ---------------------------------------------------
from utils.supabase_utils import get_supabase

# ---------------------------------------------------
# Supabase Client erzeugen
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("👤 Kundenverwaltung")
st.write("Hier kannst du Kunden hinzufügen, anzeigen und löschen.")

# ---------------------------------------------------
# Kunden laden
# ---------------------------------------------------
def load_kunden():
    try:
        data = supabase.table("kunden").select("*").execute().data
        return data if data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Kunden: {e}")
        return []

kunden = load_kunden()

# ---------------------------------------------------
# Kunden hinzufügen
# ---------------------------------------------------
st.subheader("➕ Neuen Kunden hinzufügen")

with st.form("kunden_form"):
    name = st.text_input("Name")
    adresse = st.text_input("Adresse")
    email = st.text_input("E-Mail")
    telefon = st.text_input("Telefon")

    submitted = st.form_submit_button("Speichern")

    if submitted:
        if not name:
            st.warning("Bitte mindestens einen Namen eingeben.")
        else:
            try:
                supabase.table("kunden").insert({
                    "name": name,
                    "adresse": adresse,
                    "email": email,
                    "telefon": telefon
                }).execute()
                st.success("Kunde erfolgreich gespeichert.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

# ---------------------------------------------------
# Kundenliste anzeigen
# ---------------------------------------------------
st.subheader("📋 Kundenliste")

if not kunden:
    st.info("Noch keine Kunden vorhanden.")
else:
    for k in kunden:
        with st.container():
            st.write(f"**{k['name']}**")
            st.write(f"📍 {k.get('adresse', '-')}")
            st.write(f"📧 {k.get('email', '-')}")
            st.write(f"📞 {k.get('telefon', '-')}")
            
            # Löschen-Button
            if st.button(f"Kunde löschen", key=f"del_{k['id']}"):
                try:
                    supabase.table("kunden").delete().eq("id", k["id"]).execute()
                    st.success("Kunde gelöscht.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Löschen: {e}")

            st.markdown("---")
