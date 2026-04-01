import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase, get_belege_df

st.title("📊 Dashboard – Überblick")

# -----------------------------
# DATEN LADEN
# -----------------------------
def load_finanzen():
    data = supabase.table("finanzen").select("*").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["datum", "typ", "betrag"])

    for col in ["datum", "typ", "betrag"]:
        if col not in df.columns:
            df[col] = None

    return df

def load_fahrten():
    data = supabase.table("fahrtenbuch").select("*").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["datum", "start", "ziel", "kilometer"])

    for col in ["datum", "start", "ziel", "kilometer"]:
        if col not in df.columns:
            df[col] = None

    return df

belege_df = get_belege_df()
fin_df = load_finanzen()
fahrten_df = load_fahrten()

# -----------------------------
# DATEN AUFBEREITEN
# -----------------------------
# Einnahmen
if not belege_df.empty:
    einnahmen = belege_df[belege_df["typ"] == "Rechnung"]["betrag"].sum()
else:
    einnahmen = 0

# Ausgaben
if not fin_df.empty:
    ausgaben = fin_df[fin_df["typ"] == "Ausgabe"]["betrag"].sum()
else:
    ausgaben = 0

# Gewinn
gewinn = einnahmen - ausgaben

# Kilometer
if not fahrten_df.empty:
    km = fahrten_df["kilometer"].astype(float).sum()
else:
    km = 0

# -----------------------------
# KPI-KÄSTEN
# -----------------------------
st.subheader("Kennzahlen")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Einnahmen gesamt", f"{einnahmen:.2f} €")

with col2:
    st.metric("Ausgaben gesamt", f"{ausgaben:.2f} €")

with col3:
    st.metric("Gewinn gesamt", f"{gewinn:.2f} €")

with col4:
    st.metric("Gefahrene Kilometer", f"{km:.1f} km")

# -----------------------------
# LETZTE BELEGE
# -----------------------------
st.subheader("📄 Letzte Belege")

if belege_df.empty:
    st.info("Noch keine Belege vorhanden.")
else:
    belege_df["datum"] = pd.to_datetime(belege_df["datum"], errors="coerce")
    st.dataframe(
        belege_df.sort_values("datum", ascending=False).head(5)[
            ["datum", "nr", "kunde", "typ", "betrag"]
        ]
    )

# -----------------------------
# LETZTE AUSGABEN
# -----------------------------
st.subheader("💸 Letzte Ausgaben")

if fin_df.empty:
    st.info("Noch keine Ausgaben vorhanden.")
else:
    fin_df["datum"] = pd.to_datetime(fin_df["datum"], errors="coerce")
    ausgaben_df = fin_df[fin_df["typ"] == "Ausgabe"]

    if ausgaben_df.empty:
        st.info("Keine Ausgaben vorhanden.")
    else:
        st.dataframe(
            ausgaben_df.sort_values("datum", ascending=False).head(5)[
                ["datum", "kategorie", "betrag"]
            ]
        )

# -----------------------------
# LETZTE FAHRTEN
# -----------------------------
st.subheader("🚗 Letzte Fahrten")

if fahrten_df.empty:
    st.info("Noch keine Fahrten vorhanden.")
else:
    fahrten_df["datum"] = pd.to_datetime(fahrten_df["datum"], errors="coerce")
    st.dataframe(
        fahrten_df.sort_values("datum", ascending=False).head(5)[
            ["datum", "start", "ziel", "kilometer"]
        ]
    )
