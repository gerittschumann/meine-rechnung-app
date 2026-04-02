import streamlit as st
import pandas as pd
import datetime

from utils.supabase_utils import get_supabase, get_belege_df

st.set_page_config(
    page_title="Finanzamt",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Finanzamt – Jahresübersicht")

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
# Dokumentübersicht
# ---------------------------------------------------
st.subheader("📄 Dokumente des Jahres")

df_show = df_jahr[["nummer", "typ", "summe", "datum", "pdf_url"]].sort_values("datum", ascending=False)
df_show["datum"] = df_show["datum"].dt.strftime("%d.%m.%Y")

st.dataframe(df_show, use_container_width=True)

# ---------------------------------------------------
# PDF Links anzeigen
# ---------------------------------------------------
st.subheader("📥 PDF Links")

for _, row in df_show.iterrows():
    icon = "📄" if row["typ"] == "rechnung" else "📑" if row["typ"] == "angebot" else "🧾"
    st.markdown(f"**{icon} {row['nummer']} – {row['summe']:.2f} €**")
    if row["pdf_url"]:
        st.markdown(f"[PDF öffnen]({row['pdf_url']})")
    st.markdown("---")
