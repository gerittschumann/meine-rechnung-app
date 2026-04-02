import streamlit as st
import datetime
import streamlit.components.v1 as components
from streamlit_signature_pad import st_signature_pad

from utils.supabase_utils import get_supabase
from utils.pdf_utils import create_pdf, upload_pdf_to_storage, pdf_bytes_to_data_url

st.set_page_config(
    page_title="Quittung",
    page_icon="🧾",
    layout="wide"
)

supabase = get_supabase()

st.title("🧾 Quittung erstellen")

# ---------------------------------------------------
# Kunden laden
# ---------------------------------------------------
kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden} if kunden else {}

# ---------------------------------------------------
# Positionen laden
# ---------------------------------------------------
positionen = supabase.table("positionen").select("*").execute().data
pos_dict = {p["bezeichnung"]: p for p in positionen} if positionen else {}

# ---------------------------------------------------
# Formular
# ---------------------------------------------------
st.subheader("Neue Quittung")

with st.form("quittung_form"):
    kunde_name = st.selectbox("Kunde auswählen", list(kunden_namen.keys()))
    ausgewaehlte_pos = st.multiselect("Positionen", list(pos_dict.keys()))

    gesamt = 0
    pos_eintraege = []

    for pos_name in ausgewaehlte_pos:
        pos = pos_dict[pos_name]
        menge = st.number_input(
            f"Menge für {pos_name}",
            min_value=1,
            value=1,
            key=f"menge_q_{pos_name}"
        )
        gesamtpreis = menge * pos["preis"]
        gesamt += gesamtpreis

        pos_eintraege.append({
            "position_id": pos["id"],
            "menge": menge,
            "einzelpreis": pos["preis"],
            "gesamtpreis": gesamtpreis
        })

    st.markdown(f"### 💰 Gesamtsumme: **{gesamt:.2f} €**")

    st.markdown("### ✍️ Unterschrift (funktioniert perfekt auf dem Handy)")
    unterschrift = st_signature_pad(
        key="sign_quittung",
        height=200,
        pen_color="black",
        background_color="white"
    )

    submitted = st.form_submit_button("Quittung speichern")

# ---------------------------------------------------
# Verarbeitung
# ---------------------------------------------------
if submitted:
    if not ausgewaehlte_pos:
        st.warning("Bitte mindestens eine Position auswählen.")
        st.stop()

    kunde_id = kunden_namen[kunde_name]

    # 1. Quittung speichern
    doc = supabase.table("dokumente").insert({
        "typ": "quittung",
        "kunde_id": kunde_id,
        "summe": gesamt,
        "erstellt_am": datetime.datetime.utcnow().isoformat()
    }).execute()

    doc_id = doc.data[0]["id"]

    # 2. Quittungsnummer generieren
    heute = datetime.datetime.now().strftime("%Y%m%d")
    nummer = f"Q-{heute}-{doc_id:04d}"

    supabase.table("dokumente").update({"nummer": nummer}).eq("id", doc_id).execute()

    # 3. Positionen speichern
    for p in pos_eintraege:
        p["dokument_id"] = doc_id
        supabase.table("dokument_positionen").insert(p).execute()

    # 4. Kundendaten laden
    kunde_data = supabase.table("kunden").select("*").eq("id", kunde_id).execute().data[0]

    # 5. Positionen für PDF
    pos_for_pdf = []
    for p in pos_eintraege:
        pos_info = supabase.table("positionen").select("*").eq("id", p["position_id"]).execute().data[0]
        pos_for_pdf.append({
            "bezeichnung": pos_info["bezeichnung"],
            "menge": p["menge"],
            "gesamtpreis": p["gesamtpreis"]
        })

    # 6. PDF erzeugen
    unterschrift_bytes = unterschrift if unterschrift else None

    pdf_bytes = create_pdf(
        title="Quittung",
        nummer=nummer,
        kunde=kunde_data,
        positionen=pos_for_pdf,
        summe=gesamt,
        unterschrift_bytes=unterschrift_bytes
    )

    # 7. PDF hochladen
    bucket = "pdfs"
    path = f"quittungen/{nummer}.pdf"
    pdf_url = upload_pdf_to_storage(supabase, pdf_bytes, bucket, path)

    supabase.table("dokumente").update({"pdf_url": pdf_url}).eq("id", doc_id).execute()

    st.success(f"Quittung {nummer} gespeichert.")

    # 8. PDF Vorschau
    st.subheader("📄 PDF Vorschau")
    data_url = pdf_bytes_to_data_url(pdf_bytes)

    components.html(
        f"<iframe src='{data_url}' width='100%' height='600px' style='border:none;'></iframe>",
        height=620
    )

    st.download_button(
        label="📥 PDF herunterladen",
        data=pdf_bytes,
        file_name=f"Quittung_{nummer}.pdf",
        mime="application/pdf"
    )
