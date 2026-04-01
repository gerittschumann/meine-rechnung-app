import streamlit as st
import pandas as pd
from utils.supabase_utils import supabase

st.title("⚙️ Einstellungen")

# -----------------------------
# EINSTELLUNGEN LADEN
# -----------------------------
def load_settings():
    data = supabase.table("settings").select("*").execute().data
    df = pd.DataFrame(data)

    if df.empty:
        return {
            "firma": "",
            "adresse": "",
            "km_pauschale": 0.30,
            "stundensatz": 0.0
        }

    row = df.iloc[0]

    return {
        "firma": row.get("firma", ""),
        "adresse": row.get("adresse", ""),
        "km_pauschale": row.get("km_pauschale", 0.30),
        "stundensatz": row.get("stundensatz", 0.0)
    }

settings = load_settings()

# -----------------------------
# FORMULAR
# -----------------------------
st.subheader("Firmendaten")

firma = st.text_input("Firmenname", value=settings["firma"])
adresse = st.text_area("Adresse", value=settings["adresse"])

st.subheader("Standardwerte")

km_pauschale = st.number_input("Kilometerpauschale (€)", min_value=0.0, step=0.01, value=float(settings["km_pauschale"]))
stundensatz = st.number_input("Stundensatz (€)", min_value=0.0, step=1.0, value=float(settings["stundensatz"]))

# -----------------------------
# SPEICHERN
# -----------------------------
if st.button("💾 Einstellungen speichern"):

    # Prüfen, ob es bereits einen Eintrag gibt
    existing = supabase.table("settings").select("*").execute().data

    if len(existing) == 0:
        # Neu anlegen
        supabase.table("settings").insert({
            "firma": firma,
            "adresse": adresse,
            "km_pauschale": km_pauschale,
            "stundensatz": stundensatz
        }).execute()
    else:
        # Aktualisieren
        supabase.table("settings").update({
            "firma": firma,
            "adresse": adresse,
            "km_pauschale": km_pauschale,
            "stundensatz": stundensatz
        }).eq("id", existing[0]["id"]).execute()

    st.success("Einstellungen gespeichert!")
    st.rerun()

# -----------------------------
# VORSCHAU
# -----------------------------
st.subheader("Vorschau")

st.write(f"**Firma:** {firma}")
st.write(f"**Adresse:** {adresse}")
st.write(f"**Kilometerpauschale:** {km_pauschale:.2f} €")
st.write(f"**Stundensatz:** {stundensatz:.2f} €")
