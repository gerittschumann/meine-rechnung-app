import streamlit as st
import datetime
from utils.supabase_utils import get_supabase

st.set_page_config(
    page_title="Finanzen",
    page_icon="⛽",
    layout="wide"
)

supabase = get_supabase()

st.title("⛽ Finanzen – Einnahmen & Ausgaben")

# ---------------------------------------------------
# Daten laden
# ---------------------------------------------------
def load_finanzen():
    try:
        data = supabase.table("finanzen").select("*").order("datum", desc=True).execute().data
        return data if data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Finanzen: {e}")
        return []

finanzen = load_finanzen()

# ---------------------------------------------------
# Neue Buchung
# ---------------------------------------------------
st.subheader("➕ Neue Buchung")

with st.form("fin_form"):
    typ = st.selectbox("Art", ["Einnahme", "Ausgabe"])
    betrag = st.number_input("Betrag (€)", min_value=0.0, step=0.50)
    beschreibung = st.text_input("Beschreibung")
    datum = st.date_input("Datum", datetime.date.today())

    submit = st.form_submit_button("Speichern")

if submit:
    try:
        supabase.table("finanzen").insert({
            "typ": typ.lower(),
            "betrag": betrag,
            "beschreibung": beschreibung,
            "datum": datum.isoformat()
        }).execute()

        st.success("Buchung gespeichert.")
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

monat_einnahmen = 0
monat_ausgaben = 0
jahr_einnahmen = 0
jahr_ausgaben = 0

for f in finanzen:
    try:
        d = datetime.date.fromisoformat(f["datum"])
    except:
        continue

    if d >= monat_start:
        if f["typ"] == "einnahme":
            monat_einnahmen += f["betrag"]
        else:
            monat_ausgaben += f["betrag"]

    if d >= jahr_start:
        if f["typ"] == "einnahme":
            jahr_einnahmen += f["betrag"]
        else:
            jahr_ausgaben += f["betrag"]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Monat")
    st.write(f"**Einnahmen:** {monat_einnahmen:.2f} €")
    st.write(f"**Ausgaben:** {monat_ausgaben:.2f} €")
    st.write(f"**Ergebnis:** {(monat_einnahmen - monat_ausgaben):.2f} €")

with col2:
    st.markdown("### 📆 Jahr")
    st.write(f"**Einnahmen:** {jahr_einnahmen:.2f} €")
    st.write(f"**Ausgaben:** {jahr_ausgaben:.2f} €")
    st.write(f"**Ergebnis:** {(jahr_einnahmen - jahr_ausgaben):.2f} €")

# ---------------------------------------------------
# Tabelle aller Buchungen
# ---------------------------------------------------
st.subheader("📋 Alle Buchungen")

if not finanzen:
    st.info("Noch keine Einträge vorhanden.")
else:
    for f in finanzen:
        farbe = "green" if f["typ"] == "einnahme" else "red"

        st.markdown(
            f"### <span style='color:{farbe}'>{f['typ'].capitalize()}</span>",
            unsafe_allow_html=True
        )

        st.write(f"💰 Betrag: **{f['betrag']:.2f} €**")
        st.write(f"📝 {f.get('beschreibung', '-')}")
        st.write(f"📅 {f['datum']}")

        if st.button("🗑️ Löschen", key=f"del_{f['id']}"):
            try:
                supabase.table("finanzen").delete().eq("id", f["id"]).execute()
                st.success("Eintrag gelöscht.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Fehler beim Löschen: {e}")

        st.markdown("---")
