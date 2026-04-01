import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import get_belege_df, get_positionen_df, upload_pdf_to_supabase
from utils.pdf_utils import create_document
from utils.layout_utils import whatsapp_link
from utils.offline_utils import safe_insert

st.title("🧾 Quittung zu bestehender Rechnung")

belege_df = get_belege_df()
rechnungen = belege_df[belege_df["typ"] == "Rechnung"]

if rechnungen.empty:
    st.info("Es sind noch keine Rechnungen vorhanden.")
    st.stop()

auswahl = st.selectbox(
    "Rechnung auswählen",
    rechnungen["nr"].tolist()
)

beleg = rechnungen[rechnungen["nr"] == auswahl].iloc[0]
kunde = beleg["kunde"]
adresse = beleg["adresse"]
betrag = beleg["betrag"]

st.write(f"**Kunde:** {kunde}")
st.write(f"**Adresse:** {adresse}")
st.write(f"**Rechnungsbetrag:** {betrag:.2f} €")

pos_df = get_positionen_df()
posten = pos_df[pos_df["beleg_nr"] == auswahl].to_dict(orient="records")

st.subheader("Positionen der Rechnung")
st.table(pd.DataFrame(posten))

quittungs_nr = f"{auswahl}Q"
st.write(f"**Quittungsnummer:** {quittungs_nr}")

if st.button("📄 Quittung erstellen & archivieren"):
    pdf_bytes = create_document(
        kunde,
        adresse,
        posten,
        quittungs_nr,
        "Quittung",
        sign_img=None,
        ist_vorschau=False
    )

    pdf_url = upload_pdf_to_supabase(pdf_bytes, f"{quittungs_nr}.pdf")

    safe_insert("belege", {
        "nr": quittungs_nr,
        "kunde": kunde,
        "adresse": adresse,
        "datum": datetime.now().date().isoformat(),
        "typ": "Quittung",
        "betrag": betrag,
        "stunden": None,
        "pdf_url": pdf_url,
    })

    st.success("Quittung erfolgreich erstellt und archiviert (online oder offline)!")
    st.write("Download-Link:")
    st.write(pdf_url)

    st.markdown(f"[📲 Per WhatsApp senden]({whatsapp_link(pdf_url)})")
