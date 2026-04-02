import streamlit as st
from supabase import create_client, Client
from utils.pdf_generator import generate_pdf

# Supabase Client initialisieren
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("📄 Rechnung / Angebot")

# -----------------------------
# DOKUMENT ERSTELLEN
# -----------------------------

# Dokumenttyp auswählen
typ = st.selectbox("Dokumenttyp", ["rechnung", "angebot"])

# Kunde auswählen
kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden}
kunde_name = st.selectbox("Kunde", list(kunden_namen.keys()))
kunde_id = kunden_namen[kunde_name]

# Neues Dokument erstellen
if st.button("➕ Neues Dokument erstellen"):
    res = supabase.table("dokumente").insert({
        "typ": typ,
        "kunde_id": kunde_id
    }).execute()

    new_doc = res.data[0]
    st.session_state["doc_id"] = new_doc["id"]
    st.success(f"{typ.capitalize()} wurde erstellt.")

# doc_id prüfen
doc_id = st.session_state.get("doc_id")

if not doc_id:
    st.info("Bitte ein Dokument erstellen oder auswählen.")
    st.stop()

# -----------------------------
# DOKUMENT LADEN
# -----------------------------
res_doc = supabase.table("dokumente").select("*").eq("id", doc_id).execute()
if not res_doc.data:
    st.error("Dokument wurde nicht gefunden.")
    st.stop()

dokument = res_doc.data[0]

# -----------------------------
# POSITIONEN LADEN
# -----------------------------
res_pos = supabase.table("positionen").select("*").eq("dokument_id", doc_id).execute()
positionen = res_pos.data if res_pos.data else []

# -----------------------------
# EINSTELLUNGEN LADEN
# -----------------------------
res_set = supabase.table("einstellungen").select("*").execute()
if not res_set.data:
    st.error("Bitte zuerst die Einstellungen ausfüllen.")
    st.stop()

einstellungen = res_set.data[0]

# -----------------------------
# PDF ERZEUGEN
# -----------------------------
pdf_bytes = generate_pdf(dokument, positionen, einstellungen)

# -----------------------------
# PDF VORSCHAU + DOWNLOAD
# -----------------------------
st.subheader("📄 Vorschau")

st.download_button(
    label="PDF herunterladen",
    data=pdf_bytes,
    file_name=f"{dokument['nummer']}.pdf",
    mime="application/pdf"
)

st.pdf(pdf_bytes)
