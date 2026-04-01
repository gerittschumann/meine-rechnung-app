import streamlit as st
import pandas as pd
from utils.supabase_utils import supabase

st.title("👤 Kundenverwaltung")

# -----------------------------
# KUNDEN LADEN
# -----------------------------
def load_kunden():
    data = supabase.table("kunden").select("*").order("name").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["id", "name", "adresse", "telefon", "email"])

    for col in ["id", "name", "adresse", "telefon", "email"]:
        if col not in df.columns:
            df[col] = None

    return df

kunden_df = load_kunden()

# -----------------------------
# KUNDENLISTE ANZEIGEN
# -----------------------------
st.subheader("Kundenliste")

if kunden_df.empty:
    st.info("Noch keine Kunden vorhanden.")
else:
    st.dataframe(kunden_df)

# -----------------------------
# NEUEN KUNDEN ANLEGEN
# -----------------------------
st.subheader("Neuen Kunden anlegen")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Name")
    telefon = st.text_input("Telefon")

with col2:
    email = st.text_input("E-Mail")
    adresse = st.text_area("Adresse")

if st.button("➕ Kunden speichern"):
    if name.strip() == "":
        st.error("Bitte mindestens einen Namen eingeben.")
        st.stop()

    supabase.table("kunden").insert({
        "name": name,
        "adresse": adresse,
        "telefon": telefon,
        "email": email
    }).execute()

    st.success("Kunde gespeichert!")
    st.rerun()

# -----------------------------
# KUNDEN BEARBEITEN / LÖSCHEN
# -----------------------------
st.subheader("Kunde bearbeiten oder löschen")

if kunden_df.empty:
    st.info("Keine Kunden zum Bearbeiten vorhanden.")
else:
    kunden_namen = kunden_df["name"].tolist()
    auswahl = st.selectbox("Kunde auswählen", kunden_namen)

    kunde = kunden_df[kunden_df["name"] == auswahl].iloc[0]

    new_name = st.text_input("Name", value=kunde["name"])
    new_adresse = st.text_area("Adresse", value=kunde["adresse"])
    new_telefon = st.text_input("Telefon", value=kunde["telefon"])
    new_email = st.text_input("E-Mail", value=kunde["email"])

    colA, colB = st.columns(2)

    with colA:
        if st.button("💾 Änderungen speichern"):
            supabase.table("kunden").update({
                "name": new_name,
                "adresse": new_adresse,
                "telefon": new_telefon,
                "email": new_email
            }).eq("id", kunde["id"]).execute()

            st.success("Kunde aktualisiert!")
            st.rerun()

    with colB:
        if st.button("🗑️ Kunde löschen"):
            supabase.table("kunden").delete().eq("id", kunde["id"]).execute()
            st.warning("Kunde gelöscht
