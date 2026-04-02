import streamlit as st
import datetime
import base64
from io import BytesIO
import streamlit.components.v1 as components

from utils.supabase_utils import get_supabase
from utils.pdf_utils import create_pdf, upload_pdf_to_storage, pdf_bytes_to_data_url

st.set_page_config(
    page_title="Quittung",
    page_icon="🧾",
    layout="wide"
)

supabase = get_supabase()

st.title("🧾 Quittung erstellen")

# ---------------------------------------------------
# SIGNATURE PAD (HTML CANVAS)
# ---------------------------------------------------
def signature_pad():
    html_code = """
    <style>
        #sig-pad {
            border: 2px solid black;
            border-radius: 5px;
            touch-action: none;
        }
    </style>

    <canvas id="sig-pad" width="400" height="200"></canvas>
    <br>
    <button onclick="clearPad()">Löschen</button>
    <button onclick="savePad()">Übernehmen</button>

    <script>
        var canvas = document.getElementById('sig-pad');
        var ctx = canvas.getContext('2d');
        var drawing = false;

        function getPos(e) {
            var rect = canvas.getBoundingClientRect();
            return {
                x: (e.touches ? e.touches[0].clientX : e.clientX) - rect.left,
                y: (e.touches ? e.touches[0].clientY : e.clientY) - rect.top
            };
        }

        canvas.addEventListener('mousedown', function(e) {
            drawing = true;
            var pos = getPos(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        });

        canvas.addEventListener('mousemove', function(e) {
            if (drawing) {
                var pos = getPos(e);
                ctx.lineTo(pos.x, pos.y);
                ctx.stroke();
            }
        });

        canvas.addEventListener('mouseup', function() {
            drawing = false;
        });

        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            drawing = true;
            var pos = getPos(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        });

        canvas.addEventListener('touchmove', function(e) {
            e.preventDefault();
            if (drawing) {
                var pos = getPos(e);
                ctx.lineTo(pos.x, pos.y);
                ctx.stroke();
            }
        });

        canvas.addEventListener('touchend', function() {
            drawing = false;
        });

        function clearPad() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function savePad() {
            const dataURL = canvas.toDataURL('image/png');
            window.parent.postMessage({signature: dataURL}, "*");
        }
    </script>
    """

    components.html(html_code, height=300)

    # Listener für die Unterschrift
    sig = st.session_state.get("signature_image", None)

    def _js_listener():
        components.html(
            """
            <script>
                window.addEventListener("message", (event) => {
                    if (event.data.signature) {
                        const pyMsg = event.data.signature;
                        window.parent.postMessage({pySig: pyMsg}, "*");
                    }
                });
            </script>
            """,
            height=0
        )

    _js_listener()

    return sig


# ---------------------------------------------------
# Kunden & Positionen laden
# ---------------------------------------------------
kunden = supabase.table("kunden").select("*").execute().data
kunden_namen = {k["name"]: k["id"] for k in kunden} if kunden else {}

positionen = supabase.table("positionen").select("*").execute().data
pos_dict = {p["bezeichnung"]: p for p in positionen} if positionen else {}

# ---------------------------------------------------
# Formular
# ---------------------------------------------------
st.subheader("Neue Quittung")

with st.form("quittung_form"):
    kunde_name = st.selectbox("Kunde auswählen", list(kunden_namen.keys()))
    ausgewaehlte_pos = st.multiselect("Positionen", list(pos_dict.keys()))

    gesamt = 0
    pos_eintraege = []

    for pos_name in ausgewaehlte_pos:
        pos = pos_dict[pos_name]
        menge = st.number_input(
            f"Menge für {pos_name}",
            min_value=1,
            value=1,
            key=f"menge_q_{pos_name}"
        )
        gesamtpreis = menge * pos["preis"]
        gesamt += gesamtpreis

        pos_eintraege.append({
            "position_id": pos["id"],
            "menge": menge,
            "einzelpreis": pos["preis"],
            "gesamtpreis": gesamtpreis
        })

    st.markdown(f"### 💰 Gesamtsumme: **{gesamt:.2f} €**")

    st.markdown("### ✍️ Unterschrift")
    st.info("Bitte unterschreiben und anschließend auf **Übernehmen** klicken.")

    submitted = st.form_submit_button("Quittung speichern")

# ---------------------------------------------------
# Unterschrift empfangen
# ---------------------------------------------------
if "pySig" in st.session_state:
    st.session_state["signature_image"] = st.session_state["pySig"]

sig = signature_pad()

# ---------------------------------------------------
# Verarbeitung
# ---------------------------------------------------
if submitted:
    if not ausgewaehlte_pos:
        st.warning("Bitte mindestens eine Position auswählen.")
        st.stop()

    kunde_id = kunden_namen[kunde_name]

    # 1. Quittung speichern
    doc = supabase.table("dokumente").insert({
        "typ": "quittung",
        "kunde_id": kunde_id,
        "summe": gesamt,
        "erstellt_am": datetime.datetime.utcnow().isoformat()
    }).execute()

    doc_id = doc.data[0]["id"]

    # 2. Quittungsnummer generieren
    heute = datetime.datetime.now().strftime("%Y%m%d")
    nummer = f"Q-{heute}-{doc_id:04d}"

    supabase.table("dokumente").update({"nummer": nummer}).eq("id", doc_id).execute()

    # 3. Positionen speichern
    for p in pos_eintraege:
        p["dokument_id"] = doc_id
        supabase.table("dokument_positionen").insert(p).execute()

    # 4. Kundendaten laden
    kunde_data = supabase.table("kunden").select("*").eq("id", kunde_id).execute().data[0]

    # 5. Positionen für PDF
    pos_for_pdf = []
    for p in pos_eintraege:
        pos_info = supabase.table("positionen").select("*").eq("id", p["position_id"]).execute().data[0]
        pos_for_pdf.append({
            "bezeichnung": pos_info["bezeichnung"],
            "menge": p["menge"],
            "gesamtpreis": p["gesamtpreis"]
        })

    # 6. Unterschrift verarbeiten
    unterschrift_bytes = None
    if sig:
        header, encoded = sig.split(",", 1)
        unterschrift_bytes = base64.b64decode(encoded)

    # 7. PDF erzeugen
    pdf_bytes = create_pdf(
        title="Quittung",
        nummer=nummer,
        kunde=kunde_data,
        positionen=pos_for_pdf,
        summe=gesamt,
        unterschrift_bytes=unterschrift_bytes
    )

    # 8. PDF hochladen
    bucket = "pdfs"
    path = f"quittungen/{nummer}.pdf"
    pdf_url = upload_pdf_to_storage(supabase, pdf_bytes, bucket, path)

    supabase.table("dokumente").update({"pdf_url": pdf_url}).eq("id", doc_id).execute()

    st.success(f"Quittung {nummer} gespeichert.")

    # 9. PDF Vorschau
    st.subheader("📄 PDF Vorschau")
    data_url = pdf_bytes_to_data_url(pdf_bytes)

    components.html(
        f"<iframe src='{data_url}' width='100%' height='600px' style='border:none;'></iframe>",
        height=620
    )

    st.download_button(
        label="📥 PDF herunterladen",
        data=pdf_bytes,
        file_name=f"Quittung_{nummer}.pdf",
        mime="application/pdf"
    )
