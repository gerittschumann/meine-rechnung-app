import streamlit as st
from contextlib import contextmanager

# ---------------------------------------------------
# SECTION HEADER
# ---------------------------------------------------

def section_title(title: str, icon: str = "📌"):
    """
    Einheitlicher Abschnittstitel.
    """
    st.markdown(f"### {icon} {title}")
    st.markdown("<hr>", unsafe_allow_html=True)


# ---------------------------------------------------
# INFO-BOXEN
# ---------------------------------------------------

def info_box(title: str, content: str, icon: str = "ℹ️"):
    """
    Blaue Info-Box mit Titel und Text.
    """
    st.markdown(
        f"""
        <div style="
            padding: 12px;
            border-radius: 8px;
            background-color: #e8f1ff;
            border-left: 6px solid #2b6cb0;
            margin-bottom: 15px;
            line-height: 1.5;
        ">
            <strong>{icon} {title}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


def warning_box(title: str, content: str, icon: str = "⚠️"):
    """
    Gelbe Warnbox.
    """
    st.markdown(
        f"""
        <div style="
            padding: 12px;
            border-radius: 8px;
            background-color: #fff4d6;
            border-left: 6px solid #d69e2e;
            margin-bottom: 15px;
            line-height: 1.5;
        ">
            <strong>{icon} {title}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


def success_box(title: str, content: str, icon: str = "✅"):
    """
    Grüne Erfolgsbox.
    """
    st.markdown(
        f"""
        <div style="
            padding: 12px;
            border-radius: 8px;
            background-color: #e6ffed;
            border-left: 6px solid #38a169;
            margin-bottom: 15px;
            line-height: 1.5;
        ">
            <strong>{icon} {title}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------
# CARD / BOX LAYOUT
# ---------------------------------------------------

@contextmanager
def card(title: str = "", icon: str = "📄"):
    """
    Wiederverwendbare Card-Komponente.
    Nutzung:

    with card("Kundendaten", "🧍"):
        st.write("Inhalt...")
    """
    st.markdown(
        """
        <div style="
            padding: 18px;
            border-radius: 10px;
            background-color: #fafafa;
            border: 1px solid #ddd;
            margin-bottom: 20px;
        ">
        """,
        unsafe_allow_html=True
    )

    if title:
        st.markdown(f"**{icon} {title}**")

    yield

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# HORIZONTALER TRENNER
# ---------------------------------------------------

def divider():
    """
    Einheitlicher horizontaler Trenner.
    """
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)


# ---------------------------------------------------
# SPALTEN-LAYOUT
# ---------------------------------------------------

def two_columns():
    """
    Liefert zwei gleich große Spalten zurück.
    """
    return st.columns(2)


def three_columns():
    """
    Liefert drei gleich große Spalten zurück.
    """
    return st.columns(3)


# ---------------------------------------------------
# TITEL MIT ICON
# ---------------------------------------------------

def page_title(title: str, icon: str):
    """
    Einheitlicher Seitentitel.
    """
    st.markdown(f"# {icon} {title}")
    st.markdown("<hr>", unsafe_allow_html=True)
