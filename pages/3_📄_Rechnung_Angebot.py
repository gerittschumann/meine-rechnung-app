import streamlit as st
from supabase import create_client, Client
from utils.pdf_generator import generate_pdf
import datetime
import base64

# Supabase Client
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("📄 Rechnung & Angebot")

# ---------------------------------------------------
# FUNKTION: Automatische Dokumentnummer erzeugen
# ---------------------------------------------------
def generate_document_number(typ):
    year = datetime.datetime.now().year
    prefix = "RE" if typ == "rechnung" else "AN"

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

kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden}
kunde_name = st.selectbox("Kunde", list(kunden_namen.keys()))
kunde_id = kunden_namen[kunde_name]

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
dokument = res_doc.data[0]

st.subheader(f"{dokument['typ'].capitalize()} {dokument['nummer']}")

# ---------------------------------------------------
# POSITIONEN LADEN
# ---------------------------------------------------
res_pos = supabase.table("positionen").select("*").eq("dokument_id", doc_id).execute()
positionen = res_pos.data if res_pos.data else []

# ---------------------------------------------------
# POSITIONEN ANZEIGEN
# ---------------------------------------------------
st.subheader("🛒 Positionen")

for pos in positionen:
    col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
    col1.write(pos["beschreibung"])
    col2.write(pos["menge"])
    col3.write(f"{pos['preis']:.2f} EUR")
    col4.write(f"{pos['gesamt']:.2f} EUR")

    if col5.button("❌", key=f"del_{pos['id']}"):
        supabase.table("positionen").delete().eq("id", pos["id"]).execute()
        st.rerun()

# ---------------------------------------------------
# LEISTUNGEN LADEN
# ---------------------------------------------------
leistungen = supabase.table("leistungen").select("*").execute().data
leistungsnamen = {l["bezeichnung"]: l for l in leistungen}

st.subheader("➕ Position hinzufügen")

# Dropdown für Leistungen
auswahl = st.selectbox(
    "Leistung auswählen",
    ["Manuelle Eingabe"] + list(leistungsnamen.keys())
)

# ---------------------------------------------------
# AUTOMATISCHE ÜBERNAHME ODER MANUELLE EINGABE
# ---------------------------------------------------
if auswahl != "Manuelle Eingabe":
    leistung = leistungsnamen[auswahl]

    beschreibung = st.text_input(
        "Beschreibung",
        value=leistung["bezeichnung"]
    )

    preis = st.number_input(
        "Preis (EUR)",
        min_value=0.0,
        value=float(leistung["preis"])
    )

    einheit = st.text_input(
        "Einheit",
        value=leistung.get("einheit", "")
    )

else:
    beschreibung = st.text_input("Beschreibung")
    preis = st.number_input("Preis (EUR)", min_value=0.0, value=0.0)
    einheit = st.text_input("Einheit", value="")

menge = st.number_input("Menge", min_value=1.0, value=1.0)

# ---------------------------------------------------
# POSITION SPEICHERN
# ---------------------------------------------------
if st.button("Position speichern"):
    gesamt = menge * preis

    supabase.table("positionen").insert({
        "dokument_id": doc_id,
        "beschreibung": beschreibung,
        "menge": menge,
        "preis": preis,
        "einheit": einheit,
        "gesamt": gesamt
    }).execute()

    st.success("Position gespeichert.")
    st.rerun()

# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
res_set = supabase.table("einstellungen").select("*").execute()
einstellungen = res_set.data[0]

# ---------------------------------------------------
# PDF ERZEUGEN
# ---------------------------------------------------
st.subheader("📄 PDF erzeugen")

if st.button("PDF erstellen & speichern"):
    pdf_bytes = generate_pdf(dokument, positionen, einstellungen)

    file_name = f"{dokument['nummer']}.pdf"

    supabase.storage.from_("archiv").upload(
        file_name,
        pdf_bytes,
        {"content-type": "application/pdf"}
    )

    public_url = supabase.storage.from_("archiv").get_public_url(file_name)

    supabase.table("dokumente").update({
        "pdf_url": public_url
    }).eq("id", doc_id).execute()

    st.success("PDF wurde gespeichert!")

# ---------------------------------------------------
# PDF ANZEIGEN / DOWNLOAD
# ---------------------------------------------------
if dokument.get("pdf_url"):
    st.subheader("📎 PDF")

    st.markdown(f"[📄 PDF in neuem Tab öffnen]({dokument['pdf_url']})")

    st.download_button(
        label="PDF herunterladen",
        data=base64.b64decode(base64.b64encode(pdf_bytes)),
        file_name=f"{dokument['nummer']}.pdf",
        mime="application/pdf"
    )
