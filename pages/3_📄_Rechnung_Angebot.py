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

st.title("📄 Rechnung / Angebot")

# ---------------------------------------------------
# Kunden & Positionen laden
# ---------------------------------------------------
kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden} if kunden else {}

positionen = supabase.table("positionen").select("*").execute().data
pos_dict = {p["bezeichnung"]: p for p in positionen} if positionen else {}

# ---------------------------------------------------
# Formular: Neues Dokument
# ---------------------------------------------------
st.subheader("🧾 Neues Dokument erstellen")

with st.form("dokument_form"):
    art = st.selectbox("Dokumentart", ["Rechnung", "Angebot"])

    if not kunden_namen:
        st.warning("Keine Kunden vorhanden. Bitte zuerst Kunden anlegen.")
        submitted = False
    else:
        kunde_name = st.selectbox("Kunde auswählen", list(kunden_namen.keys()))

        st.markdown("### Positionen auswählen")
        ausgewaehlte_pos = st.multiselect(
            "Positionen",
            list(pos_dict.keys())
        )

        gesamt = 0
        pos_eintraege = []

        for pos_name in ausgewaehlte_pos:
            pos = pos_dict[pos_name]

            menge = st.number_input(
                f"Menge für {pos_name}",
                min_value=1,
                value=1,
                key=f"menge_{pos_name}"
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

        submitted = st.form_submit_button("Speichern")

# ---------------------------------------------------
# Verarbeitung: Speichern + PDF + Storage + Nummer
# ---------------------------------------------------
if submitted:
    if not ausgewaehlte_pos:
        st.warning("Bitte mindestens eine Position auswählen.")
    else:
        try:
            kunde_id = kunden_namen[kunde_name]

            # 1. Dokument zunächst ohne Nummer speichern
            doc = supabase.table("dokumente").insert({
                "typ": art.lower(),          # "rechnung" / "angebot"
                "kunde_id": kunde_id,
                "summe": gesamt,
                "erstellt_am": datetime.datetime.utcnow().isoformat()
            }).execute()

            doc_id = doc.data[0]["id"]

            # 2. Nummer generieren (z.B. R-20260402-0001)
            prefix = "R" if art == "Rechnung" else "A"
            heute = datetime.datetime.now().strftime("%Y%m%d")
            nummer = f"{prefix}-{heute}-{doc_id:04d}"

            supabase.table("dokumente").update({
                "nummer": nummer
            }).eq("id", doc_id).execute()

            # 3. Positionen speichern
            for p in pos_eintraege:
                p["dokument_id"] = doc_id
                supabase.table("dokument_positionen").insert(p).execute()

            # 4. Kundendaten laden
            kunde_data = supabase.table("kunden").select("*").eq("id", kunde_id).execute().data[0]

            # 5. Positionen für PDF aufbereiten
            pos_for_pdf = []
            for p in pos_eintraege:
                pos_info = supabase.table("positionen").select("*").eq("id", p["position_id"]).execute().data[0]
                pos_for_pdf.append({
                    "bezeichnung": pos_info["bezeichnung"],
                    "menge": p["menge"],
                    "gesamtpreis": p["gesamtpreis"]
                })

            # 6. PDF erzeugen
            pdf_bytes = create_pdf(
                kunde=kunde_data,
                positionen=pos_for_pdf,
                summe=gesamt,
                dokument_typ=art,
                dokument_nr=nummer
            )

            # 7. PDF in Supabase Storage hochladen
            bucket_name = "pdfs"
            path = f"{art.lower()}/{nummer}.pdf"
            pdf_url = upload_pdf_to_storage(supabase, pdf_bytes, bucket_name, path)

            # 8. PDF-URL im Dokument speichern
            supabase.table("dokumente").update({
                "pdf_url": pdf_url
            }).eq("id", doc_id).execute()

            st.success(f"{art} {nummer} erfolgreich gespeichert.")

            # 9. PDF-Vorschau + Download
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

        except Exception as e:
            st.error(f"Fehler beim Erstellen des Dokuments: {e}")

# ---------------------------------------------------
# Übersicht: Rechnungen & Angebote
# ---------------------------------------------------
st.markdown("---")
st.subheader("📚 Übersicht: Rechnungen & Angebote")

filter_art = st.selectbox("Anzeigen:", ["Alle", "Rechnungen", "Angebote"])

query = supabase.table("dokumente").select("*")

if filter_art == "Rechnungen":
    query = query.eq("typ", "rechnung")
elif filter_art == "Angebote":
    query = query.eq("typ", "angebot")

docs = query.order("erstellt_am", desc=True).execute().data

if not docs:
    st.info("Noch keine Dokumente vorhanden.")
else:
    for d in docs:
        kunde_name = "-"
        try:
            kd = supabase.table("kunden").select("name").eq("id", d["kunde_id"]).execute().data
            if kd:
                kunde_name = kd[0]["name"]
        except:
            pass

        with st.container():
            st.write(f"**{d.get('nummer', 'Ohne Nummer')}** – {d['typ'].capitalize()}")
            st.write(f"👤 {kunde_name} | 💰 {d.get('summe', 0):.2f} € | 📅 {d.get('erstellt_am', '-')}")
            if d.get("pdf_url"):
                st.write(f"🔗 PDF: {d['pdf_url']}")

            col1, col2 = st.columns(2)

            with col1:
                if d.get("pdf_url"):
                    if st.button("📄 PDF im Browser öffnen", key=f"open_{d['id']}"):
                        st.markdown(f"[PDF öffnen]({d['pdf_url']})", unsafe_allow_html=True)

            with col2:
                # Optional: später z.B. löschen / duplizieren
                pass

            st.markdown("---")
