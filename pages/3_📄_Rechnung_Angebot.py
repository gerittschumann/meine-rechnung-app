import streamlit as st
from supabase import create_client, Client
from utils.pdf_generator import generate_pdf

# Supabase Client initialisieren
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# Dokument-ID laden (aus Session oder URL)
doc_id = st.session_state.get("doc_id")

if not doc_id:
    st.error("Kein Dokument ausgewählt.")
    st.stop()

# 1. Dokument laden
res_doc = supabase.table("dokumente").select("*").eq("id", doc_id).execute()
if not res_doc.data:
    st.error("Dokument wurde nicht gefunden.")
    st.stop()

dokument = res_doc.data[0]

# 2. Positionen laden
res_pos = supabase.table("positionen").select("*").eq("dokument_id", doc_id).execute()
positionen = res_pos.data if res_pos.data else []

# 3. Einstellungen laden
res_set = supabase.table("einstellungen").select("*").execute()
if not res_set.data:
    st.error("Bitte zuerst die Einstellungen ausfüllen.")
    st.stop()

einstellungen = res_set.data[0]

# 4. PDF erzeugen
pdf_bytes = generate_pdf(dokument, positionen, einstellungen)

# 5. Vorschau + Download
st.subheader("📄 Vorschau")

st.download_button(
    label="PDF herunterladen",
    data=pdf_bytes,
    file_name=f"{dokument['nummer']}.pdf",
    mime="application/pdf"
)

st.pdf(pdf_bytes)
