# ---------------------------------------------------
# EINSTELLUNGEN LADEN
# ---------------------------------------------------
res_set = supabase.table("einstellungen").select("*").execute()
einstellungen = res_set.data[0]

# ---------------------------------------------------
# PDF ERZEUGEN
# ---------------------------------------------------
st.subheader("📄 PDF erzeugen")

if st.button("PDF erstellen & speichern"):
    # PDF erzeugen
    pdf_bytes = generate_pdf(dokument, positionen, einstellungen)

    # PDF in Session speichern (für Download/Vorschau)
    st.session_state["pdf_bytes"] = pdf_bytes

    # Dateiname
    file_name = f"{dokument['nummer']}.pdf"

    # PDF in Supabase-Bucket 'archiv' hochladen
    supabase.storage.from_("archiv").upload(
        file_name,
        pdf_bytes,
        {"content-type": "application/pdf"}
    )

    # Öffentliche URL holen
    public_url = supabase.storage.from_("archiv").get_public_url(file_name)

    # URL im Dokument speichern
    supabase.table("dokumente").update({
        "pdf_url": public_url
    }).eq("id", doc_id).execute()

    st.success("PDF wurde gespeichert!")

# ---------------------------------------------------
# PDF ANZEIGEN / DOWNLOAD
# ---------------------------------------------------
if dokument.get("pdf_url"):
    st.subheader("📎 PDF")

    # Download-Button nur, wenn pdf_bytes in der Session liegt
    if "pdf_bytes" in st.session_state:
        st.download_button(
            label="PDF herunterladen",
            data=st.session_state["pdf_bytes"],
            file_name=f"{dokument['nummer']}.pdf",
            mime="application/pdf"
        )

    # Link zum Öffnen im neuen Tab
    st.markdown(f"[📄 PDF in neuem Tab öffnen]({dokument['pdf_url']})")
