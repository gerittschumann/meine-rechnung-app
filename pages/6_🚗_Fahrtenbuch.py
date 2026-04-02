import streamlit as st
import datetime
from utils.supabase_utils import get_supabase

st.set_page_config(
    page_title="Fahrtenbuch",
    page_icon="🚗",
    layout="wide"
)

supabase = get_supabase()

st.title("🚗 Fahrtenbuch")

# ---------------------------------------------------
# Fahrten laden
# ---------------------------------------------------
def load_fahrten():
    try:
        data = supabase.table("fahrtenbuch").select("*").order("datum", desc=True).execute().data
        return data if data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Fahrten: {e}")
        return []

fahrten = load_fahrten()

# ---------------------------------------------------
# Neue Fahrt eintragen
# ---------------------------------------------------
st.subheader("➕ Neue Fahrt eintragen")

with st.form("fahrt_form"):
    datum = st.date_input("Datum", datetime.date.today())
    start = st.text_input("Startadresse")
    ziel = st.text_input("Zieladresse")
    kilometer = st.number_input("Gefahrene Kilometer", min_value=0.0, step=0.1)

    submit = st.form_submit_button("Speichern")

if submit:
    try:
        supabase.table("fahrtenbuch").insert({
            "datum": datum.isoformat(),
            "start": start,
            "ziel": ziel,
            "kilometer": kilometer
        }).execute()

        st.success("Fahrt gespeichert.")
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")

# ---------------------------------------------------
# Auswertung
# ---------------------------------------------------
st.subheader("📊 Auswertung")

heute = datetime.date.today()
monat_start = heute.replace(day=1)
jahr_start = heute.replace(month=1, day=1)

monat_km = 0
jahr_km = 0
gesamt_km = 0

for f in fahrten:
    try:
        d = datetime.date.fromisoformat(f["datum"])
    except:
        continue

    km = f.get("kilometer", 0)
    gesamt_km += km

    if d >= monat_start:
        monat_km += km

    if d >= jahr_start:
        jahr_km += km

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🚗 Kilometer (Monat)", f"{monat_km:.1f} km")

with col2:
    st.metric("📆 Kilometer (Jahr)", f"{jahr_km:.1f} km")

with col3:
    st.metric("📍 Gesamt", f"{gesamt_km:.1f} km")

# ---------------------------------------------------
# Fahrtenliste
# ---------------------------------------------------
st.subheader("📋 Alle Fahrten")

if not fahrten:
    st.info("Noch keine Fahrten eingetragen.")
else:
    for f in fahrten:
        st.markdown(f"### 🚗 {f['datum']}")
        st.write(f"**Start:** {f['start']}")
        st.write(f"**Ziel:** {f['ziel']}")
        st.write(f"**Kilometer:** {f['kilometer']} km")

        if st.button("🗑️ Löschen", key=f"del_{f['id']}"):
            try:
                supabase.table("fahrtenbuch").delete().eq("id", f["id"]).execute()
                st.success("Fahrt gelöscht.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Fehler beim Löschen: {e}")

        st.markdown("---")
