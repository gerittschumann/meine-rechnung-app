import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase
from utils.offline_utils import safe_insert

st.title("🚗 Fahrtenbuch")

def load_fahrten():
    data = supabase.table("fahrtenbuch").select("*").order("datum", desc=True).execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["id", "datum", "start", "ziel", "zweck", "kilometer"])

    for col in ["id", "datum", "start", "ziel", "zweck", "kilometer"]:
        if col not in df.columns:
            df[col] = None

    return df

fahrten_df = load_fahrten()

st.subheader("Neue Fahrt eintragen")

col1, col2 = st.columns(2)

with col1:
    datum = st.date_input("Datum", datetime.now())
    start = st.text_input("Start")
    ziel = st.text_input("Ziel")

with col2:
    zweck = st.text_input("Zweck")
    kilometer = st.number_input("Kilometer", min_value=0.0, step=0.1)

if st.button("💾 Fahrt speichern"):
    if start.strip() == "" or ziel.strip() == "":
        st.error("Bitte Start und Ziel eingeben.")
        st.stop()

    safe_insert("fahrtenbuch", {
        "datum": datum.isoformat(),
        "start": start,
        "ziel": ziel,
        "zweck": zweck,
        "kilometer": kilometer
    })

    st.success("Fahrt gespeichert (online oder offline)!")
    st.rerun()

st.subheader("Alle Fahrten")

if fahrten_df.empty:
    st.info("Noch keine Fahrten eingetragen.")
else:
    fahrten_df["datum"] = pd.to_datetime(fahrten_df["datum"], errors="coerce")
    st.dataframe(fahrten_df)

st.subheader("Kilometerpauschale")

if fahrten_df.empty:
    st.info("Keine Daten für Berechnung vorhanden.")
else:
    gesamt_km = fahrten_df["kilometer"].astype(float).sum()
    pauschale = gesamt_km * 0.30

    st.write(f"**Gesamtkilometer:** {gesamt_km:.1f} km")
    st.write(f"**Kilometerpauschale (0,30 €):** {pauschale:.2f} €")

st.subheader("Fahrt löschen")

if fahrten_df.empty:
    st.info("Keine Fahrten zum Löschen vorhanden.")
else:
    ids = fahrten_df["id"].tolist()
    labels = [
        f"{row['datum']} – {row['start']} → {row['ziel']} – {row['kilometer']} km"
        for _, row in fahrten_df.iterrows()
    ]

    auswahl = st.selectbox("Fahrt auswählen", options=list(zip(ids, labels)), format_func=lambda x: x[1])

    if st.button("🗑️ Fahrt löschen"):
        supabase.table("fahrtenbuch").delete().eq("id", auswahl[0]).execute()
        st.warning("Fahrt gelöscht!")
        st.rerun()
