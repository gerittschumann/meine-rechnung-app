import streamlit as st
from supabase import create_client
from utils.pdf_generator import generate_pdf
import datetime
from io import BytesIO

# ---------------------------------------------------
# SUPABASE INITIALISIEREN
# ---------------------------------------------------
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("📄 Rechnung / Angebot erstellen")

# ---------------------------------------------------
# FUNKTION: AUTOMATISCHE RECHNUNGSNUMMER
# ---------------------------------------------------
def generate_next_number(dokument_typ):
    jahr = datetime.datetime.now().year

    result = (
        supabase.table("dokumente")
        .select("nummer")
        .eq("typ", dokument_typ)
        .like("nummer", f"%{jahr}%")
        .order("nummer", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        letzte = result.data[0]["nummer"]  # z.B. RE-2024-0007
        laufend = int(letzte.split("-")[2]) + 1
    else:
        laufend = 1

    prefix = dokument_typ.upper()[0:2]  # RE / AN
    return f"{prefix}-{jahr}-{laufend:04d}"


# ---------------------------------------------------
# FORMULAR FÜR DOKUMENTDATEN
# ---------------------------------------------------
dokument_typ = st.selectbox("Dokumenttyp", ["rechnung", "angebot"])
kunde_id = st.text_input("Kunden-ID")

st.write("### Positionen")
anzahl = st.number_input("Anzahl Positionen", min_value=1, max_value=20, value=1)

positionen = []
for i in range(anzahl):
    st.write(f"**Position {i+1}**")
    beschreibung = st.text_input(f"Beschreibung {i+1}")
    menge = st.number_input(f"Menge {i+1}", min_value=1, value=1)
    preis = st.number_input(f"Preis {i+1}", min_value=0.0, value=0.0)
    gesamt = menge * preis

    positionen.append({
        "beschreibung": beschreibung,
        "menge": menge,
        "preis": preis,
        "gesamt": gesamt
    })


# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
einstellungen = supabase.table("einstellungen").select("*").single().execute().data


# ---------------------------------------------------
# PDF ERZEUGEN (ABER NICHT SPEICHERN!)
# ---------------------------------------------------
if st.button("PDF Vorschau erzeugen"):
    dokument = {
        "typ": dokument_typ,
        "kunde_id": kunde_id,
        "nummer": "VORSCHAU",
        "summe": sum([p["gesamt"] for p in positionen])
    }

    pdf_bytes = generate_pdf(dokument, positionen, einstellungen)
    st.session_state["pdf_bytes"] = pdf_bytes


# ---------------------------------------------------
# VORSCHAU ANZEIGEN
# ---------------------------------------------------
if "pdf_bytes" in st.session_state:
    st.write("### 📄 Vorschau")
    st.download_button(
        "PDF herunterladen",
        data=st.session_state["pdf_bytes"],
        file_name="vorschau.pdf"
    )

    st.write("### PDF Vorschau im Browser")
    st.pdf(st.session_state["pdf_bytes"])

    st.write("---")

    # ---------------------------------------------------
    # SPEICHERN ERST BEI KLICK
    # ---------------------------------------------------
    if st.button("Dokument speichern"):

        # 1. Automatische Rechnungsnummer erzeugen
        nummer = generate_next_number(dokument_typ)

        # 2. PDF hochladen
        path = f"{nummer}.pdf"

        supabase.storage.from_("archiv").update(
            path,
            st.session_state["pdf_bytes"],
            {"content-type": "application/pdf"}
        )

        # 3. Öffentliche URL erzeugen
        public_url = supabase.storage.from_("archiv").get_public_url(path)

        # 4. In Datenbank speichern
        supabase.table("dokumente").insert({
            "typ": dokument_typ,
            "nummer": nummer,
            "kunde_id": kunde_id,
            "pdf_url": public_url,
            "summe": sum([p["gesamt"] for p in positionen])
        }).execute()

        st.success(f"Dokument gespeichert! Nummer: {nummer}")
