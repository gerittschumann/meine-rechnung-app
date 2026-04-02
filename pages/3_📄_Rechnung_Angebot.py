import streamlit as st

st.set_page_config(
    page_title="Rechnung & Angebot",
    page_icon="📄",
    layout="wide"
)

from utils.supabase_utils import get_supabase

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
# Formular
# ---------------------------------------------------
st.subheader("🧾 Dokument erstellen")

with st.form("dokument_form"):
    art = st.selectbox("Dokumentart", ["Rechnung", "Angebot"])

    kunde = st.selectbox("Kunde auswählen", list(kunden_namen.keys()))

    st.markdown("### Positionen auswählen")

    ausgewaehlte_pos = st.multiselect(
        "Positionen",
        list(pos_dict.keys())
    )

    # Dynamische Eingabe für jede Position
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

    if submitted:
        # Dokument speichern
        doc = supabase.table("dokumente").insert({
            "typ": art.lower(),
            "kunde_id": kunden_namen[kunde],
            "summe": gesamt
        }).execute()

        doc_id = doc.data[0]["id"]

        # Positionen speichern
        for p in pos_eintraege:
            p["dokument_id"] = doc_id
            supabase.table("dokument_positionen").insert(p).execute()

        st.success(f"{art} erfolgreich gespeichert!")
        st.info("PDF‑Erstellung folgt im nächsten Schritt.")
