import streamlit as st


def get_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    if st.session_state.theme == "dark":
        return {
            "is_dark": True,
            "BG": "#0A0F1E",
            "CARD": "#111827",
            "TEXT": "#E2E8F0",
            "SUBTEXT": "#94A3B8",
            "ACCENT": "#00D4FF",
            "GRID": "#1F2937",
            "BORDER": "#1F2937",
            "SIDEBAR": "#0D1117",
            "MAP_STYLE": "carto-darkmatter",
        }

    return {
        "is_dark": False,
        "BG": "#F0F4F8",
        "CARD": "#FFFFFF",
        "TEXT": "#0F172A",
        "SUBTEXT": "#475569",
        "ACCENT": "#0077B6",
        "GRID": "#CBD5E1",
        "BORDER": "#CBD5E1",
        "SIDEBAR": "#E2E8F0",
        "MAP_STYLE": "carto-positron",
    }


def get_chart_layout(t):
    return {
        "paper_bgcolor": t["CARD"],
        "plot_bgcolor": t["CARD"],
        "font": {
            "color": t["TEXT"]
        },
        "title_font": {
            "color": t["TEXT"],
            "size": 16
        },
        "margin": {
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20
        },
        "legend": {
            "bgcolor": t["CARD"],
            "font": {
                "color": t["TEXT"]
            }
        }
    }


def render_sidebar(t):
    with st.sidebar:

        st.title("🌿 India AQI")
        st.caption("Air Quality Dashboard")

        st.divider()

        # Theme button
        if t["is_dark"]:
            button_text = "☀️ Light Mode"
        else:
            button_text = "🌙 Dark Mode"

        if st.button(button_text, use_container_width=True):
            if t["is_dark"]:
                st.session_state.theme = "light"
            else:
                st.session_state.theme = "dark"

            st.rerun()

        st.divider()

        st.subheader("🔽 Filters")

        year_range = st.slider(
            "📅 Year Range",
            min_value=2009,
            max_value=2024,
            value=(2009, 2024)
        )

        st.divider()

        st.caption(
            "India AQI Dashboard\n\n"
            "Python • Pandas • Plotly • Streamlit"
        )

    return year_range


def render_footer(t):
    st.divider()

    st.caption(
        "📊 India AQI Dashboard | "
        "Python • Pandas • Plotly • Streamlit | "
        "Data: CPCB via Kaggle"
    )


def aqi_bucket_color(bucket):
    colors = {
        "Good": "#2DC653",
        "Satisfactory": "#A8E063",
        "Moderate": "#F9C74F",
        "Poor": "#F4A261",
        "Very Poor": "#E63946",
        "Severe": "#6C1515"
    }

    return colors.get(bucket, "#94A3B8")


def bar_color_from_aqi(aqi):
    if aqi <= 50:
        return "#2DC653"
    elif aqi <= 100:
        return "#A8E063"
    elif aqi <= 200:
        return "#F9C74F"
    elif aqi <= 300:
        return "#F4A261"
    elif aqi <= 400:
        return "#E63946"
    else:
        return "#6C1515"


MONTHS = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

BUCKET_ORDER = [
    "Good",
    "Satisfactory",
    "Moderate",
    "Poor",
    "Very Poor",
    "Severe"
]
