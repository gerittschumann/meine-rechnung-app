import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

from utils.supabase_utils import get_supabase, get_belege_df

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard")

supabase = get_supabase()

# ---------------------------------------------------
# Daten laden
# ---------------------------------------------------
df = get_belege_df(supabase)

if df.empty:
    st.info("Noch keine Dokumente vorhanden.")
    st.stop()

# ---------------------------------------------------
# Grunddaten vorbereiten
# ---------------------------------------------------
df["datum"] = pd.to_datetime(df["erstellt_am"], errors="coerce")
df["monat"] = df["datum"].dt.to_period("M").astype(str)
df["jahr"] = df["datum"].dt.year

heute = datetime.date.today()
aktuelles_jahr = heute.year
aktueller_monat = heute.strftime("%Y-%m")

df_jahr = df[df["jahr"] == aktuelles_jahr]
df_monat = df[df["monat"] == aktueller_monat]

# ---------------------------------------------------
# KPIs
# ---------------------------------------------------
gesamt_umsatz = df[df["typ"] == "rechnung"]["summe"].sum()
umsatz_jahr = df_jahr[df_jahr["typ"] == "rechnung"]["summe"].sum()
umsatz_monat = df_monat[df_monat["typ"] == "rechnung"]["summe"].sum()

anzahl_rechnungen = len(df[df["typ"] == "rechnung"])
anzahl_angebote = len(df[df["typ"] == "angebot"])
anzahl_quittungen = len(df[df["typ"] == "quittung"])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Gesamtumsatz", f"{gesamt_umsatz:.2f} €")

with col2:
    st.metric("📅 Umsatz (Monat)", f"{umsatz_monat:.2f} €")

with col3:
    st.metric("📆 Umsatz (Jahr)", f"{umsatz_jahr:.2f} €")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric("📄 Rechnungen", anzahl_rechnungen)

with col5:
    st.metric("📑 Angebote", anzahl_angebote)

with col6:
    st.metric("🧾 Quittungen", anzahl_quittungen)

# ---------------------------------------------------
# Umsatz pro Monat (Diagramm)
# ---------------------------------------------------
st.subheader("📈 Umsatzentwicklung pro Monat")

umsatz_pro_monat = (
    df[df["typ"] == "rechnung"]
    .groupby("monat")["summe"]
    .sum()
    .reset_index()
)

if not umsatz_pro_monat.empty:
    fig = px.bar(
        umsatz_pro_monat,
        x="monat",
        y="summe",
        title="Umsatz pro Monat",
        labels={"monat": "Monat", "summe": "Umsatz (€)"},
        text_auto=".2f"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Noch keine Rechnungen vorhanden.")

# ---------------------------------------------------
# Dokumentverteilung (Kreisdiagramm)
# ---------------------------------------------------
st.subheader("📊 Dokumentverteilung")

verteilung = df["typ"].value_counts().reset_index()
verteilung.columns = ["typ", "anzahl"]

fig2 = px.pie(
    verteilung,
    names="typ",
    values="anzahl",
    title="Verteilung der Dokumentarten",
    color="typ",
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# Letzte Dokumente
# ---------------------------------------------------
st.subheader("📄 Letzte Dokumente")

df_sorted = df.sort_values("datum", ascending=False).head(10)

for _, row in df_sorted.iterrows():
    typ_icon = "📄" if row["typ"] == "rechnung" else "📑" if row["typ"] == "angebot" else "🧾"

    st.markdown(f"### {typ_icon} {row['nummer']}")
    st.write(f"👤 Kunde-ID: {row['kunde_id']}")
    st.write(f"💰 Summe: **{row['summe']:.2f} €**")
    st.write(f"📅 Datum: {row['datum'].strftime('%d.%m.%Y')}")

    if row.get("pdf_url"):
        st.markdown(f"[📄 PDF öffnen]({row['pdf_url']})")

    st.markdown("---")
