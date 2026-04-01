import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase

st.title("📊 Finanzamt – Jahresübersicht")

# -----------------------------
# DATEN LADEN
# -----------------------------
def load_belege():
    data = supabase.table("belege").select("*").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["nr", "kunde", "adresse", "datum", "typ", "betrag"])

    for col in ["nr", "kunde", "adresse", "datum", "typ", "betrag"]:
        if col not in df.columns:
            df[col] = None

    return df

def load_finanzen():
    data = supabase.table("finanzen").select("*").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["datum", "typ", "kategorie", "betrag"])

    for col in ["datum", "typ", "kategorie", "betrag"]:
        if col not in df.columns:
            df[col] = None

    return df

belege_df = load_belege()
fin_df = load_finanzen()

# -----------------------------
# DATEN AUFBEREITEN
# -----------------------------
if not belege_df.empty:
    belege_df["datum"] = pd.to_datetime(belege_df["datum"], errors="coerce")
    belege_df["monat"] = belege_df["datum"].dt.month
    einnahmen = belege_df[belege_df["typ"] == "Rechnung"]
else:
    einnahmen = pd.DataFrame(columns=["monat", "betrag"])

if not fin_df.empty:
    fin_df["datum"] = pd.to_datetime(fin_df["datum"], errors="coerce")
    fin_df["monat"] = fin_df["datum"].dt.month
    ausgaben = fin_df[fin_df["typ"] == "Ausgabe"]
else:
    ausgaben = pd.DataFrame(columns=["monat", "betrag"])

# -----------------------------
# MONATLICHE SUMMEN
# -----------------------------
monats_einnahmen = einnahmen.groupby("monat")["betrag"].sum()
monats_ausgaben = ausgaben.groupby("monat")["betrag"].sum()

# Fehlende Monate ergänzen
for m in range(1, 13):
    if m not in monats_einnahmen.index:
        monats_einnahmen.loc[m] = 0
    if m not in monats_ausgaben.index:
        monats_ausgaben.loc[m] = 0

monats_einnahmen = monats_einnahmen.sort_index()
monats_ausgaben = monats_ausgaben.sort_index()

gewinn = monats_einnahmen - monats_ausgaben

# -----------------------------
# ANZEIGE
# -----------------------------
st.subheader("📅 Monatliche Einnahmen / Ausgaben / Gewinn")

df_chart = pd.DataFrame({
    "Einnahmen": monats_einnahmen,
    "Ausgaben": monats_ausgaben,
    "Gewinn": gewinn
})

st.line_chart(df_chart)

# -----------------------------
# JAHRESSUMMEN
# -----------------------------
st.subheader("📘 Jahresübersicht")

jahres_einnahmen = monats_einnahmen.sum()
jahres_ausgaben = monats_ausgaben.sum()
jahres_gewinn = gewinn.sum()

st.write(f"**Einnahmen gesamt:** {jahres_einnahmen:.2f} €")
st.write(f"**Ausgaben gesamt:** {jahres_ausgaben:.2f} €")
st.write(f"**Gewinn gesamt:** {jahres_gewinn:.2f} €")

# -----------------------------
# RÜCKLAGE
# -----------------------------
st.subheader("💰 Rücklage für Einkommensteuer")

steuersatz = st.slider("Einkommensteuer-Satz (%)", 10, 45, 25)

ruecklage = jahres_gewinn * (steuersatz / 100)

st.write(f"**Empfohlene Rücklage:** {ruecklage:.2f} €")
