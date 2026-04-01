import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase, upload_pdf_to_supabase
from utils.pdf_utils import create_document

st.title("📄 Rechnung / Angebot erstellen")

# -----------------------------
# WARENKORB INITIALISIEREN
# -----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# -----------------------------
# KUNDENDATEN
# -----------------------------
st.subheader("Kundendaten")

kunde = st.text_input("Kunde")
adresse = st.text_area("Adresse")

# -----------------------------
# POSITION HINZUFÜGEN
# -----------------------------
st.subheader("Position hinzufügen")

col1, col2, col3, col4 = st.columns(4)

with col1:
    leistung = st.text_input("Leistung")

with col2:
    menge = st.number_input("Menge", min_value=1, step=1)

with col3:
    preis = st.number_input("Preis (€)", min_value=0.0, step=0.10)

with col4:
    if st.button("➕ Hinzufügen"):
        gesamt = menge * preis
        st.session_state.cart.append({
            "leistung": leistung,
            "menge": menge,
            "preis": preis,
            "gesamt": gesamt
        })
        st.success("Position hinzugefügt!")

# -----------------------------
# WARENKORB ANZEIGEN
# -----------------------------
st.subheader("Aktuelle Positionen")

if len(st.session_state.cart) == 0:
    st.info("Noch keine Positionen hinzugefügt.")
else:
    df = pd.DataFrame(st.session_state.cart)
    st.table(df)

# -----------------------------
# DOKUMENTTYP
# -----------------------------
st.subheader("Dokumenttyp wählen")

typ = st.selectbox("Typ", ["Rechnung", "Angebot"])

# -----------------------------
# SPEICHERN
# -----------------------------
if st.button("📄 Dokument erstellen & speichern"):

    if kunde.strip() == "" or adresse.strip() == "":
        st.error("Bitte Kundendaten ausfüllen.")
        st.stop()

    if len(st.session_state.cart) == 0:
        st.error("Bitte mindestens eine Position hinzufügen.")
        st.stop()

    # Nummer erzeugen
    jahr = datetime.now().year
    nummer = f"{typ[:2].upper()}-{jahr}-{int(datetime.now().timestamp())}"

    # PDF erzeugen
    pdf_bytes = create_document(
        kunde,
        adresse,
        st.session_state.cart,
        nummer,
        typ,
        sign_img=None,
        ist_vorschau=False
    )

    # PDF hochladen
    pdf_url = upload_pdf_to_supabase(pdf_bytes, f"{nummer}.pdf")

    # In Supabase speichern
    supabase.table("belege").insert({
        "nr": nummer,
        "kunde": kunde,
        "adresse": adresse,
        "datum": datetime.now().date().isoformat(),
        "typ": typ,
        "betrag": sum([p["gesamt"] for p in st.session_state.cart]),
        "stunden": None,
        "pdf_url": pdf_url
    }).execute()

    # Positionen speichern
    for p in st.session_state.cart:
        supabase.table("positionen").insert({
            "beleg_nr": nummer,
            "leistung": p["leistung"],
            "menge": p["menge"],
            "preis": p["preis"],
            "gesamt": p["gesamt"]
        }).execute()

    st.success(f"{typ} erfolgreich erstellt!")
    st.write("Download-Link:")
    st.write(pdf_url)

    st.session_state.cart = []
