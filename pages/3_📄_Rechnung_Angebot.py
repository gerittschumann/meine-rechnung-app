import streamlit as st
import datetime
import streamlit.components.v1 as components

from utils.supabase_utils import get_supabase
from utils.pdf_utils import create_pdf, upload_pdf_to_storage, pdf_bytes_to_data_url

st.set_page_config(
    page_title="Rechnung & Angebot",
    page_icon="📄",
    layout="wide"
)

supabase = get_supabase()

st.title("📄 Rechnung / Angebot erstellen")

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
# Warenkorb in Session State
# ---------------------------------------------------
if "warenkorb" not in st.session_state:
    st.session_state["warenkorb"] = []

def warenkorb_hinzufuegen(pos_name, menge):
    pos = pos_dict[pos_name]
    st.session_state["warenkorb"].append({
        "id": pos["id"],
        "bezeichnung": pos_name,
        "menge": menge,
        "einzelpreis": pos["preis"],
        "gesamtpreis": menge * pos["preis"]
    })

def warenkorb_loeschen():
    st.session_state["warenkorb"] = []

def warenkorb_entfernen(index):
    st.session_state["warenkorb"].pop(index)

# ---------------------------------------------------
# Formular: Positionen hinzufügen
# ---------------------------------------------------
st.subheader("🧾 Positionen auswählen")

with st.form("pos_form"):
    pos_name = st.selectbox("Position auswählen", list(pos_dict.keys()))
    menge = st.number_input("Menge", min_value=1, value=1)
    add = st.form_submit_button("Zum Warenkorb hinzufügen")

    if add:
        warenkorb_hinzufuegen(pos_name, menge)
        st.success("Position hinzugefügt.")

# ---------------------------------------------------
# Warenkorb anzeigen
# ---------------------------------------------------
st.subheader("🛒 Warenkorb")

gesamt = 0

if not st.session_state["warenkorb"]:
    st.info("Warenkorb ist leer.")
else:
    for i, item in enumerate(st.session_state["warenkorb"]):
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])

        with col1:
            st.write(f"**{item['bezeichnung']}**")

        with col2:
            neue_menge = st.number_input(
                f"Menge {i}",
                min_value=1,
                value=item["menge"],
                key=f"edit_menge_{i}"
            )

        with col3:
            st.write(f"{item['gesamtpreis']:.2f} €")

        with col4:
            if st.button("❌", key=f"del_{i}"):
                warenkorb_entfernen(i)
                st.experimental_rerun()

        # Menge aktualisieren
        if neue_menge != item["menge"]:
            item["menge"] = neue_menge
            item["gesamtpreis"] = neue_menge * item["einzelpreis"]

        gesamt += item["gesamtpreis"]

    st.markdown(f"### 💰 Gesamtsumme: **{gesamt:.2f} €**")

    if st.button("🗑️ Warenkorb leeren"):
        warenkorb_loeschen()
        st.experimental_rerun()

# ---------------------------------------------------
# Dokument erstellen
# ---------------------------------------------------
st.subheader("📄 Dokument erstellen")

with st.form("dokument_form"):
    art = st.selectbox("Dokumentart", ["Rechnung", "Angebot"])
    kunde_name = st.selectbox("Kunde auswählen", list(kunden_namen.keys()))

    speichern = st.form_submit_button("Dokument speichern")

if speichern:
    if not st.session_state["warenkorb"]:
        st.warning("Warenkorb ist leer.")
    else:
        kunde_id = kunden_namen[kunde_name]

        # 1. Dokument speichern
        doc = supabase.table("dokumente").insert({
            "typ": art.lower(),
            "kunde_id": kunde_id,
            "summe": gesamt,
            "erstellt_am": datetime.datetime.utcnow().isoformat()
        }).execute()

        doc_id = doc.data[0]["id"]

        # 2. Nummer generieren
        prefix = "R" if art == "Rechnung" else "A"
        heute = datetime.datetime.now().strftime("%Y%m%d")
        nummer = f"{prefix}-{heute}-{doc_id:04d}"

        supabase.table("dokumente").update({"nummer": nummer}).eq("id", doc_id).execute()

        # 3. Positionen speichern
        for item in st.session_state["warenkorb"]:
            supabase.table("dokument_positionen").insert({
                "dokument_id": doc_id,
                "position_id": item["id"],
                "menge": item["menge"],
                "einzelpreis": item["einzelpreis"],
                "gesamtpreis": item["gesamtpreis"]
            }).execute()

        # 4. Kundendaten laden
        kunde_data = supabase.table("kunden").select("*").eq("id", kunde_id).execute().data[0]

        # 5. PDF erzeugen
        pos_for_pdf = [
            {
                "bezeichnung": item["bezeichnung"],
                "menge": item["menge"],
                "gesamtpreis": item["gesamtpreis"]
            }
            for item in st.session_state["warenkorb"]
        ]

        pdf_bytes = create_pdf(
            title=art,
            nummer=nummer,
            kunde=kunde_data,
            positionen=pos_for_pdf,
            summe=gesamt
        )

        # 6. PDF hochladen
        bucket = "pdfs"
        path = f"{art.lower()}/{nummer}.pdf"
        pdf_url = upload_pdf_to_storage(supabase, pdf_bytes, bucket, path)

        supabase.table("dokumente").update({"pdf_url": pdf_url}).eq("id", doc_id).execute()

        # 7. Warenkorb leeren
        warenkorb_loeschen()

        st.success(f"{art} {nummer} gespeichert.")

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
            file_name=f"{art}_{nummer}.pdf",
            mime="application/pdf"
        )

# ---------------------------------------------------
# Dokumente Übersicht
# ---------------------------------------------------
st.markdown("---")
st.subheader("📚 Übersicht")

filter_art = st.selectbox("Anzeigen:", ["Alle", "Rechnungen", "Angebote"])

query = supabase.table("dokumente").select("*")

if filter_art == "Rechnungen":
    query = query.eq("typ", "rechnung")
elif filter_art == "Angebote":
    query = query.eq("typ", "angebot")

docs = query.order("erstellt_am", desc=True).execute().data

if not docs:
    st.info("Keine Dokumente vorhanden.")
else:
    for d in docs:
        kunde = supabase.table("kunden").select("name").eq("id", d["kunde_id"]).execute().data
        kunde_name = kunde[0]["name"] if kunde else "-"

        st.write(f"### {d['nummer']} – {d['typ'].capitalize()}")
        st.write(f"👤 {kunde_name} | 💰 {d['summe']:.2f} € | 📅 {d['erstellt_am']}")

        if d.get("pdf_url"):
            st.markdown(f"[📄 PDF öffnen]({d['pdf_url']})")

        st.markdown("---")
