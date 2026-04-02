import streamlit as st
from supabase import create_client, Client

# Supabase Client
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("⚙️ Leistungen verwalten")

# ---------------------------------------------------
# LEISTUNGEN LADEN
# ---------------------------------------------------
res = supabase.table("leistungen").select("*").order("id").execute()
leistungen = res.data if res.data else []

st.subheader("➕ Neue Leistung hinzufügen")

bezeichnung = st.text_input("Bezeichnung")
preis = st.number_input("Preis (€)", min_value=0.0, value=0.0)
einheit = st.text_input("Einheit (optional)", value="")

if st.button("Speichern"):
    supabase.table("leistungen").insert({
        "bezeichnung": bezeichnung,
        "preis": preis,
        "einheit": einheit
    }).execute()
    st.success("Leistung gespeichert.")
    st.rerun()

# ---------------------------------------------------
# LEISTUNGEN LISTE
# ---------------------------------------------------
st.subheader("📋 Leistungenliste")

if not leistungen:
    st.info("Noch keine Leistungen vorhanden.")
else:
    for l in leistungen:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
        col1.write(l["bezeichnung"])
        col2.write(f"{l['preis']:.2f} €")
        col3.write(l.get("einheit", ""))

        if col4.button("❌", key=f"del_{l['id']}"):
            supabase.table("leistungen").delete().eq("id", l["id"]).execute()
            st.rerun()
