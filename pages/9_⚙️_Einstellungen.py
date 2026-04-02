import streamlit as st
from supabase import create_client, Client

# Supabase Client
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("⚙️ Einstellungen")

# Einstellungen laden
res = supabase.table("einstellungen").select("*").execute()

if res.data:
    einstellungen = res.data[0]
    einstellungen_id = einstellungen["id"]
else:
    einstellungen = {}
    einstellungen_id = None

# Formular
with st.form("einstellungen_form"):
    st.subheader("Firmendaten")
    firmenname = st.text_input("Firmenname", einstellungen.get("firmenname", ""))
    adresse = st.text_area("Adresse", einstellungen.get("adresse", ""))
    telefon = st.text_input("Telefon", einstellungen.get("telefon", ""))
    email = st.text_input("E-Mail", einstellungen.get("email", ""))
    website = st.text_input("Website", einstellungen.get("website", ""))
    steuernummer = st.text_input("Steuernummer", einstellungen.get("steuernummer", ""))

    st.subheader("Bankdaten")
    kontoinhaber = st.text_input("Kontoinhaber", einstellungen.get("kontoinhaber", ""))
    iban = st.text_input("IBAN", einstellungen.get("iban", ""))
    bic = st.text_input("BIC", einstellungen.get("bic", ""))

    st.subheader("Rechtliches")
    kleinunternehmer_hinweis = st.text_area(
        "Kleinunternehmer-Hinweis",
        einstellungen.get("kleinunternehmer_hinweis", "Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.")
    )

    st.subheader("Individuelle Texte")
    text_rechnung = st.text_area("Text für Rechnungen", einstellungen.get("text_rechnung", ""))
    text_angebot = st.text_area("Text für Angebote", einstellungen.get("text_angebot", ""))
    text_quittung = st.text_area("Text für Quittungen", einstellungen.get("text_quittung", ""))

    st.subheader("AGB & Logo")
    agb = st.text_area("AGB", einstellungen.get("agb", ""))
    logo_url = st.text_input("Logo URL", einstellungen.get("logo_url", ""))

    submitted = st.form_submit_button("Speichern")

# Speichern
if submitted:
    daten = {
        "firmenname": firmenname,
        "adresse": adresse,
        "telefon": telefon,
        "email": email,
        "website": website,
        "steuernummer": steuernummer,
        "kontoinhaber": kontoinhaber,
        "iban": iban,
        "bic": bic,
        "kleinunternehmer_hinweis": kleinunternehmer_hinweis,
        "text_rechnung": text_rechnung,
        "text_angebot": text_angebot,
        "text_quittung": text_quittung,
        "agb": agb,
        "logo_url": logo_url
    }

    if einstellungen_id:
        supabase.table("einstellungen").update(daten).eq("id", einstellungen_id).execute()
        st.success("Einstellungen aktualisiert.")
    else:
        supabase.table("einstellungen").insert(daten).execute()
        st.success("Einstellungen gespeichert.")
