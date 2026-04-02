import streamlit as st
from utils.supabase_utils import get_supabase

st.set_page_config(
    page_title="Einstellungen",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Einstellungen")

supabase = get_supabase()

# ---------------------------------------------------
# Firmeninfos laden
# ---------------------------------------------------
def load_settings():
    try:
        data = supabase.table("einstellungen").select("*").execute().data
        if data:
            return data[0]
        return {}
    except Exception as e:
        st.error(f"Fehler beim Laden der Einstellungen: {e}")
        return {}

settings = load_settings()

# ---------------------------------------------------
# Formular
# ---------------------------------------------------
st.subheader("🏢 Firmeninformationen")

with st.form("settings_form"):
    firmenname = st.text_input("Firmenname", settings.get("firmenname", ""))
    adresse = st.text_area("Adresse", settings.get("adresse", ""))
    telefon = st.text_input("Telefon", settings.get("telefon", ""))
    email = st.text_input("E-Mail", settings.get("email", ""))
    agb = st.text_area("AGB", settings.get("agb", ""), height=200)

    submit = st.form_submit_button("Speichern")

if submit:
    try:
        if settings:
            supabase.table("einstellungen").update({
                "firmenname": firmenname,
                "adresse": adresse,
                "telefon": telefon,
                "email": email,
                "agb": agb
            }).eq("id", settings["id"]).execute()
        else:
            supabase.table("einstellungen").insert({
                "firmenname": firmenname,
                "adresse": adresse,
                "telefon": telefon,
                "email": email,
                "agb": agb
            }).execute()

        st.success("Einstellungen gespeichert.")
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")

# ---------------------------------------------------
# Logo Upload
# ---------------------------------------------------
st.subheader("🖼️ Firmenlogo")

uploaded_logo = st.file_uploader("Logo hochladen", type=["png", "jpg", "jpeg"])

if uploaded_logo:
    try:
        file_bytes = uploaded_logo.read()
        file_path = f"logos/{uploaded_logo.name}"

        supabase.storage.from_("pdfs").upload(file_path, file_bytes)

        logo_url = supabase.storage.from_("pdfs").get_public_url(file_path)

        if settings:
            supabase.table("einstellungen").update({"logo_url": logo_url}).eq("id", settings["id"]).execute()

        st.success("Logo hochgeladen.")
        st.image(logo_url, width=200)

    except Exception as e:
        st.error(f"Fehler beim Hochladen des Logos: {e}")

# ---------------------------------------------------
# Logo anzeigen
# ---------------------------------------------------
if settings.get("logo_url"):
    st.image(settings["logo_url"], width=200)
