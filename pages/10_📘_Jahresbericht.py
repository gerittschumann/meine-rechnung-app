import streamlit as st
import pandas as pd
import datetime

from utils.supabase_utils import get_supabase, get_belege_df
from utils.pdf_utils import create_pdf, upload_pdf_to_storage, pdf_bytes_to_data_url

st.set_page_config(
    page_title="Jahresbericht",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Jahresbericht")

# ---------------------------------------------------
# Supabase Client
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# Daten laden
# ---------------------------------------------------
df = get_belege_df(supabase)

if df.empty:
    st.info("Noch keine Dokumente vorhanden.")
    st.stop()

# ---------------------------------------------------
# Daten vorbereiten
# ---------------------------------------------------
df["datum"] = pd.to_datetime(df["erstellt_am"], errors="coerce")
df["jahr"] = df["datum"].dt.year

aktuelles_jahr = datetime.date.today().year
df_jahr = df[df["jahr"] == aktuelles_jahr]

# ---------------------------------------------------
# Einnahmen / Ausgaben / Gewinn
# ---------------------------------------------------
einnahmen = df_jahr[df_jahr["typ"] == "rechnung"]["summe"].sum()
ausgaben = df_jahr[df_jahr["typ"] == "ausgabe"]["summe"].sum() if "ausgabe" in df_jahr["typ"].unique() else 0
gewinn = einnahmen - ausgaben

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Einnahmen", f"{einnahmen:.2f} €")

with col2:
    st.metric("📉 Ausgaben", f"{ausgaben:.2f} €")

with col3:
    st.metric("📈 Gewinn", f"{gewinn:.2f} €")

# ---------------------------------------------------
# Jahresbericht PDF erzeugen
# ---------------------------------------------------
st.subheader("📄 Jahresbericht als PDF")

if st.button("PDF erzeugen"):
    try:
        # PDF erstellen
        pdf_bytes = create_pdf(
            title=f"Jahresbericht {aktuelles_jahr}",
            nummer=f"J-{aktuelles_jahr}",
            kunde={"name": "Interner Bericht"},
            positionen=[],
            summe=einnahmen,
            unterschrift_bytes=None
        )

        # PDF hochladen
        bucket = "pdfs"
        path = f"jahresberichte/J-{aktuelles_jahr}.pdf"
        pdf_url = upload_pdf_to_storage(supabase, pdf_bytes, bucket, path)

        st.success("PDF erfolgreich erstellt.")
        st.markdown(f"[📄 PDF öffnen]({pdf_url})")

        # Vorschau
        data_url = pdf_bytes_to_data_url(pdf_bytes)
        st.components.v1.html(
            f"<iframe src='{data_url}' width='100%' height='600px' style='border:none;'></iframe>",
            height=620
        )

    except Exception as e:
        st.error(f"Fehler beim Erstellen des PDFs: {e}")

# ---------------------------------------------------
# Dokumentliste
# ---------------------------------------------------
st.subheader("📋 Dokumente des Jahres")

df_show = df_jahr[["nummer", "typ", "summe", "datum", "pdf_url"]].sort_values("datum", ascending=False)
df_show["datum"] = df_show["datum"].dt.strftime("%d.%m.%Y")

st.dataframe(df_show, use_container_width=True)
