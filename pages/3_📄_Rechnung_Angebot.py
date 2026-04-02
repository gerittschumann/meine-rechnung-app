import streamlit as st
from supabase import create_client, Client
from utils.pdf_generator import generate_pdf
import datetime

# Supabase Client
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("📄 Rechnung / Angebot")

# ---------------------------------------------------
# FUNKTION: Automatische Dokumentnummer erzeugen
# ---------------------------------------------------
def generate_document_number(typ):
    year = datetime.datetime.now().year
    prefix = "RE" if typ == "rechnung" else "AN"

    # Letzte Nummer finden
    res = supabase.table("dokumente") \
        .select("nummer") \
        .like("nummer", f"{prefix}-{year}-%") \
        .order("nummer", desc=True) \
        .limit(1) \
        .execute()

    if res.data:
        last_num = int(res.data[0]["nummer"].split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}-{year}-{new_num:04d}"

# ---------------------------------------------------
# DOKUMENT ERSTELLEN
# ---------------------------------------------------
typ = st.selectbox("Dokumenttyp", ["rechnung", "angebot"])

# Kunden laden
kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden}
kunde_name = st.selectbox("Kunde", list(kunden_namen.keys()))
kunde_id = kunden_namen[kunde_name]

# Neues Dokument erstellen
if st.button("➕ Neues Dokument erstellen"):
    nummer = generate_document_number(typ)

    res = supabase.table("dokumente").insert({
        "typ": typ,
        "kunde_id": kunde_id,
        "nummer": nummer
    }).execute()

    new_doc = res.data[0]
    st.session_state["doc_id"] = new_doc["id"]
    st.success(f"{typ.capitalize()} {nummer} wurde erstellt.")

# ---------------------------------------------------
# DOKUMENT LADEN
# ---------------------------------------------------
doc_id = st.session_state.get("doc_id")

if not doc_id:
    st.info("Bitte ein Dokument erstellen oder auswählen.")
    st.stop()

res_doc = supabase.table("dokumente").select("*").eq("id", doc_id).execute()
if not res_doc.data:
    st.error("Dokument wurde nicht gefunden.")
    st.stop()

dokument = res_doc.data[0]

# ---------------------------------------------------
# POSITIONEN LADEN
# ---------------------------------------------------
res_pos = supabase.table("positionen").select("*").eq("dokument_id", doc_id).execute()
positionen = res_pos.data if res_pos.data else []

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
res_set = supabase.table("einstellungen").select("*").execute()
if not res_set.data:
    st.error("Bitte zuerst die Einstellungen ausfüllen.")
    st.stop()

einstellungen = res_set.data[0]

# ---------------------------------------------------
# PDF ERZEUGEN
# ---------------------------------------------------
pdf_bytes = generate_pdf(dokument, positionen, einstellungen)

# ---------------------------------------------------
# PDF VORSCHAU + DOWNLOAD
# ---------------------------------------------------
st.subheader("📄 Vorschau")

st.download_button(
    label="PDF herunterladen",
    data=pdf_bytes,
    file_name=f"{dokument['nummer']}.pdf",
    mime="application/pdf"
)

st.pdf(pdf_bytes)
