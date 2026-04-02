import streamlit as st
import pandas as pd
from utils.supabase_utils import get_supabase, get_belege_df

st.set_page_config(
    page_title="Archiv",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Archiv – Alle Dokumente")

# ---------------------------------------------------
# Supabase Client
# ---------------------------------------------------
supabase = get_supabase()

# ---------------------------------------------------
# Belege laden
# ---------------------------------------------------
df = get_belege_df(supabase)

if df.empty:
    st.info("Noch keine Dokumente vorhanden.")
    st.stop()

# ---------------------------------------------------
# Daten vorbereiten
# ---------------------------------------------------
df["datum"] = pd.to_datetime(df["erstellt_am"], errors="coerce")
df = df.sort_values("datum", ascending=False)

df["datum"] = df["datum"].dt.strftime("%d.%m.%Y")

# ---------------------------------------------------
# Tabelle anzeigen
# ---------------------------------------------------
st.subheader("📄 Alle Dokumente")

df_show = df[["nummer", "typ", "summe", "datum", "pdf_url"]]

st.dataframe(df_show, use_container_width=True)

# ---------------------------------------------------
# PDF Links
# ---------------------------------------------------
st.subheader("📥 PDF Links")

for _, row in df_show.iterrows():
    icon = "📄" if row["typ"] == "rechnung" else "📑" if row["typ"] == "angebot" else "🧾"
    st.markdown(f"### {icon} {row['nummer']}")
    st.write(f"💰 Summe: {row['summe']:.2f} €")
    st.write(f"📅 Datum: {row['datum']}")

    if row["pdf_url"]:
        st.markdown(f"[PDF öffnen]({row['pdf_url']})")

    st.markdown("---")
