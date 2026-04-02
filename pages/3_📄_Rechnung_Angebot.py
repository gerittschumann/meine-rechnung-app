import streamlit as st
from utils.db import get_connection, generate_next_number
from utils.pdf_generator import generate_pdf
import pandas as pd
import base64

st.set_page_config(
    page_title="📄 Rechnung / Angebot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Rechnung oder Angebot erstellen")

# ---------------------------------------------------
# DB VERBINDUNG
# ---------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# ---------------------------------------------------
# AUSWAHL: RECHNUNG ODER ANGEBOT
# ---------------------------------------------------
dokument_typ = st.radio(
    "Dokumenttyp auswählen",
    ["rechnung", "angebot"],
    horizontal=True
)

# ---------------------------------------------------
# KUNDEN LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM kunden ORDER BY name ASC")
kunden = cur.fetchall()

if not kunden:
    st.warning("⚠️ Du musst zuerst einen Kunden anlegen.")
    st.stop()

kunden_namen = [f"{k['id']} – {k['name']}" for k in kunden]
kunde_auswahl = st.selectbox("Kunde auswählen", kunden_namen)

kunde_id = int(kunde_auswahl.split(" – ")[0])

# ---------------------------------------------------
# DOKUMENTNUMMER
# ---------------------------------------------------
nummer = generate_next_number(dokument_typ)
st.write(f"**Nummer:** {nummer}")

# ---------------------------------------------------
# LEISTUNGSKATALOG LADEN
# ---------------------------------------------------
cur.execute("SELECT * FROM leistungen ORDER BY name ASC")
leistungsliste = cur.fetchall()
leistungsnamen = [l["name"] for l in leistungsliste]

st.subheader("➕ Position hinzufügen")

auswahl = st.selectbox("Leistung auswählen", ["-- auswählen --"] + leistungsnamen)

if auswahl != "-- auswählen --":
    leistung = next(l for l in leistungsliste if l["name"] == auswahl)

    beschreibung = st.text_input("Beschreibung", value=leistung["beschreibung"])
    menge = st.number_input("Menge", min_value=1.0, step=1.0)
    preis = st.number_input("Preis (€)", value=leistung["preis"], step=0.5)
    einheit = st.text_input("Einheit", value=leistung["einheit"])

    gesamt = menge * preis
    st.write(f"**Gesamt: {gesamt:.2f} €**")

    if st.button("Position speichern"):
        cur.execute("""
            INSERT INTO positionen (dokument_id, beschreibung, menge, preis, gesamt)
            VALUES (NULL, ?, ?, ?, ?)
        """, (beschreibung, menge, preis, gesamt))
        conn.commit()
        st.success("Position gespeichert.")
        st.experimental_rerun()

# ---------------------------------------------------
# GESPEICHERTE POSITIONEN ANZEIGEN
# ---------------------------------------------------
st.subheader("📋 Aktuelle Positionen")

cur.execute("""
    SELECT * FROM positionen
    WHERE dokument_id IS NULL
""")
positionen = cur.fetchall()

if not positionen:
    st.info("Noch keine Positionen hinzugefügt.")
else:
    df = pd.DataFrame(positionen)
    df.columns = ["ID", "Dokument-ID", "Beschreibung", "Menge", "Preis (€)", "Gesamt (€)"]
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------
# SUMME BERECHNEN
# ---------------------------------------------------
summe = sum([p["gesamt"] for p in positionen]) if positionen else 0
st.subheader(f"💶 Gesamtsumme: {summe:.2f} €")

# ---------------------------------------------------
# PDF-VORSCHAU (NICHT SPEICHERN)
# ---------------------------------------------------
st.write("---")
st.subheader("👁️ Vorschau anzeigen (ohne Speichern)")

if st.button("Vorschau anzeigen"):
    # PDF erzeugen (Preview-Modus)
    pdf_bytes = generate_pdf(
        {
            "typ": dokument_typ,
            "nummer": nummer,
            "kunde_id": kunde_id,
            "summe": summe,
            "preview": True
        },
        positionen,
        {}
    )

    b64 = base64.b64encode(pdf_bytes).decode()
    pdf_iframe = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900px"></iframe>'
    st.markdown(pdf_iframe, unsafe_allow_html=True)

# ---------------------------------------------------
# DOKUMENT ABSCHLIESSEN (SPEICHERN)
# ---------------------------------------------------
st.write("---")
st.subheader(f"📄 {dokument_typ.capitalize()} final erstellen")

if st.button(f"{dokument_typ.capitalize()} speichern"):
    # Dokument speichern
    cur.execute("""
        INSERT INTO dokumente (typ, nummer, kunde_id, summe)
        VALUES (?, ?, ?, ?)
    """, (dokument_typ, nummer, kunde_id, summe))
    conn.commit()

    # ID der neuen Rechnung holen
    cur.execute("SELECT id FROM dokumente ORDER BY id DESC LIMIT 1")
    dokument_id = cur.fetchone()["id"]

    # Positionen zuordnen
    cur.execute("""
        UPDATE positionen
        SET dokument_id = ?
        WHERE dokument_id IS NULL
    """, (dokument_id,))
    conn.commit()

    st.success(f"{dokument_typ.capitalize()} erfolgreich erstellt!")
    st.balloons()

conn.close()
