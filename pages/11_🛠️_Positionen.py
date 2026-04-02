import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="📈 Positionen",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Positionen – Alle Einzelposten aus Rechnungen, Angeboten & Quittungen")

st.write("""
Hier findest du eine vollständige Übersicht aller Positionen aus allen Dokumenten.
Du kannst filtern nach:
- Dokumenttyp
- Jahr
- Kunden-ID
""")

# ---------------------------------------------------
# DATEN LADEN
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT 
        p.id,
        d.typ,
        d.nummer,
        d.kunde_id,
        p.beschreibung,
        p.menge,
        p.preis,
        p.gesamt,
        d.erstellt_am
    FROM positionen p
    JOIN dokumente d ON p.dokument_id = d.id
    ORDER BY d.erstellt_am DESC
""")
rows = cur.fetchall()

conn.close()

if not rows:
    st.info("Noch keine Positionen vorhanden.")
    st.stop()

df = pd.DataFrame(rows)
df.columns = [
    "Positions-ID",
    "Dokumenttyp",
    "Dokumentnummer",
    "Kunden-ID",
    "Beschreibung",
    "Menge",
    "Preis (€)",
    "Gesamt (€)",
    "Erstellt am"
]

# ---------------------------------------------------
# FILTER
# ---------------------------------------------------
st.subheader("🔍 Filter")

col1, col2, col3 = st.columns(3)

with col1:
    typ_filter = st.selectbox("Dokumenttyp", ["Alle", "rechnung", "angebot", "quittung"])

with col2:
    jahre = sorted(list({d["Erstellt am"][:4] for d in df.to_dict("records")}))
    jahr_filter = st.selectbox("Jahr", ["Alle"] + jahre)

with col3:
    kunde_filter = st.text_input("Kunden-ID (optional)")

df_filtered = df.copy()

if typ_filter != "Alle":
    df_filtered = df_filtered[df_filtered["Dokumenttyp"] == typ_filter]

if jahr_filter != "Alle":
    df_filtered = df_filtered[df_filtered["Erstellt am"].str.startswith(jahr_filter)]

if kunde_filter.strip() != "":
    df_filtered = df_filtered[df_filtered["Kunden-ID"].astype(str) == kunde_filter.strip()]

# ---------------------------------------------------
# TABELLE
# ---------------------------------------------------
st.subheader("📋 Gefilterte Positionen")

st.dataframe(df_filtered, use_container_width=True)

# ---------------------------------------------------
# SUMMEN
# ---------------------------------------------------
summe = df_filtered["Gesamt (€)"].sum()

st.metric("💶 Summe aller gefilterten Positionen", f"{summe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.write("---")

# ---------------------------------------------------
# EXPORT
# ---------------------------------------------------
st.subheader("📥 Export")

csv_data = df_filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 CSV herunterladen",
    data=csv_data,
    file_name="positionen_export.csv",
    mime="text/csv"
)
