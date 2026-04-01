import streamlit as st
import pandas as pd
from utils.supabase_utils import get_belege_df

st.title("📦 Archiv – Alle Belege")

# -----------------------------
# BELEGE LADEN
# -----------------------------
df = get_belege_df()

if df.empty:
    st.info("Noch keine Belege vorhanden.")
    st.stop()

# Datum konvertieren
df["datum"] = pd.to_datetime(df["datum"], errors="coerce")

# -----------------------------
# FILTER
# -----------------------------
st.subheader("Filter")

col1, col2, col3 = st.columns(3)

with col1:
    typ_filter = st.selectbox("Typ", ["Alle", "Rechnung", "Angebot", "Quittung"])

with col2:
    kunde_filter = st.text_input("Kunde (optional)")

with col3:
    sortierung = st.selectbox("Sortieren nach", ["Datum absteigend", "Datum aufsteigend"])

# Filter anwenden
filtered = df.copy()

if typ_filter != "Alle":
    filtered = filtered[filtered["typ"] == typ_filter]

if kunde_filter.strip() != "":
    filtered = filtered[filtered["kunde"].str.contains(kunde_filter, case=False, na=False)]

# Sortierung
if sortierung == "Datum absteigend":
    filtered = filtered.sort_values("datum", ascending=False)
else:
    filtered = filtered.sort_values("datum", ascending=True)

# -----------------------------
# ANZEIGE
# -----------------------------
st.subheader("Belege")

if filtered.empty:
    st.info("Keine Belege für diese Filter gefunden.")
else:
    # PDF-Link anklickbar machen
    filtered_display = filtered.copy()
    filtered_display["PDF"] = filtered_display["pdf_url"].apply(lambda x: f"[Öffnen]({x})")

    st.write(
        filtered_display[["datum", "nr", "kunde", "typ", "betrag", "PDF"]]
        .rename(columns={
            "datum": "Datum",
            "nr": "Nummer",
            "kunde": "Kunde",
            "typ": "Typ",
            "betrag": "Betrag (€)"
        })
        .to_markdown(index=False)
    )
