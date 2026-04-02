import streamlit as st
from utils.supabase_utils import get_supabase

st.set_page_config(
    page_title="Positionen",
    page_icon="🛠️",
    layout="wide"
)

supabase = get_supabase()

st.title("🛠️ Positionen verwalten")

# ---------------------------------------------------
# Positionen laden
# ---------------------------------------------------
def load_positionen():
    try:
        data = supabase.table("positionen").select("*").order("id").execute().data
        return data if data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Positionen: {e}")
        return []

positionen = load_positionen()

# ---------------------------------------------------
# Neue Position hinzufügen
# ---------------------------------------------------
st.subheader("➕ Neue Position hinzufügen")

with st.form("pos_form"):
    bezeichnung = st.text_input("Bezeichnung")
    preis = st.number_input("Preis (€)", min_value=0.0, step=0.50)

    submitted = st.form_submit_button("Speichern")

    if submitted:
        if not bezeichnung:
            st.warning("Bitte eine Bezeichnung eingeben.")
        else:
            try:
                supabase.table("positionen").insert({
                    "bezeichnung": bezeichnung,
                    "preis": preis
                }).execute()
                st.success("Position erfolgreich gespeichert.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

# ---------------------------------------------------
# Positionenliste anzeigen
# ---------------------------------------------------
st.subheader("📋 Positionenliste")

if not positionen:
    st.info("Noch keine Positionen vorhanden.")
else:
    for p in positionen:
        with st.container():
            st.write(f"### {p['bezeichnung']}")
            st.write(f"💰 Preis: **{p['preis']:.2f} €**")

            col1, col2 = st.columns(2)

            # ---------------------------------------------------
            # Bearbeiten
            # ---------------------------------------------------
            with col1:
                if st.button("✏️ Bearbeiten", key=f"edit_{p['id']}"):
                    st.session_state["edit_pos_id"] = p["id"]

            # ---------------------------------------------------
            # Löschen
            # ---------------------------------------------------
            with col2:
                if st.button("🗑️ Löschen", key=f"del_{p['id']}"):
                    try:
                        supabase.table("positionen").delete().eq("id", p["id"]).execute()
                        st.success("Position gelöscht.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Fehler beim Löschen: {e}")

            st.markdown("---")

# ---------------------------------------------------
# Bearbeitungsformular anzeigen
# ---------------------------------------------------
if "edit_pos_id" in st.session_state:
    edit_id = st.session_state["edit_pos_id"]

    st.subheader("✏️ Position bearbeiten")

    # Position laden
    pos = supabase.table("positionen").select("*").eq("id", edit_id).execute().data[0]

    with st.form("edit_pos_form"):
        bezeichnung = st.text_input("Bezeichnung", value=pos["bezeichnung"])
        preis = st.number_input("Preis (€)", min_value=0.0, step=0.50, value=float(pos["preis"]))

        save_edit = st.form_submit_button("Änderungen speichern")
        cancel_edit = st.form_submit_button("Abbrechen")

        if save_edit:
            try:
                supabase.table("positionen").update({
                    "bezeichnung": bezeichnung,
                    "preis": preis
                }).eq("id", edit_id).execute()

                st.success("Position erfolgreich aktualisiert.")
                del st.session_state["edit_pos_id"]
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Fehler beim Aktualisieren: {e}")

        if cancel_edit:
            del st.session_state["edit_pos_id"]
            st.experimental_rerun()
