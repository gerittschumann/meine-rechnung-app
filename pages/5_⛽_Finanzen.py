import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_utils import supabase
from utils.offline_utils import safe_insert

st.title("⛽ Ausgaben & Einnahmen")

def load_fin():
    data = supabase.table("finanzen").select("*").order("datum", desc=True).execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["id", "datum", "typ", "kategorie", "referenz", "betrag"])

    for col in ["id", "datum", "typ", "kategorie", "referenz", "betrag"]:
        if col not in df.columns:
            df[col] = None

    return df

fin_df = load_fin()

st.subheader("Neuen Eintrag hinzufügen")

col1, col2 = st.columns(2)

with col1:
    datum = st.date_input("Datum", datetime.now())
    typ = st.selectbox("Typ", ["Ausgabe", "Einnahme"])
    kategorie = st.text_input("Kategorie (z.B. Diesel, Werkzeug, Material, Sonstiges)")

with col2:
    referenz = st.text_input("Beschreibung / Referenz")
    betrag = st.number_input("Betrag (€)", min_value=0.0, step=0.10)

if st.button("💾 Eintrag speichern"):
    if kategorie.strip() == "":
        st.error("Bitte eine Kategorie eingeben.")
        st.stop()

    safe_insert("finanzen", {
        "datum": datum.isoformat(),
        "typ": typ,
        "kategorie": kategorie,
        "referenz": referenz,
        "betrag": betrag
    })

    st.success("Eintrag gespeichert (online oder offline)!")
    st.rerun()

st.subheader("Letzte Einträge")

if fin_df.empty:
    st.info("Noch keine Finanzdaten vorhanden.")
else:
    fin_df["datum"] = pd.to_datetime(fin_df["datum"], errors="coerce")
    st.dataframe(fin_df)

st.subheader("Eintrag löschen")

if fin_df.empty:
    st.info("Keine Einträge zum Löschen vorhanden.")
else:
    ids = fin_df["id"].tolist()
    labels = [f"{row['datum']} – {row['typ']} – {row['betrag']}€" for _, row in fin_df.iterrows()]

    auswahl = st.selectbox("Eintrag auswählen", options=list(zip(ids, labels)), format_func=lambda x: x[1])

    if st.button("🗑️ Eintrag löschen"):
        supabase.table("finanzen").delete().eq("id", auswahl[0]).execute()
        st.warning("Eintrag gelöscht!")
        st.rerun()
