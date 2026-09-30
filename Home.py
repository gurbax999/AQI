import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_loader import load_all_data
from Theme import (
    get_theme,
    get_chart_layout,
    render_sidebar,
    render_footer,
    BUCKET_ORDER,
    aqi_bucket_color
)


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="India AQI Dashboard",
    page_icon="🌿",
    layout="wide"
)

t = get_theme()
CL = get_chart_layout(t)

year_range = render_sidebar(t)


# --------------------------------------------------
# Load data
# --------------------------------------------------

with st.spinner("🌿 Loading data..."):
    df, stations, pollutants = load_all_data()

df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🌿 India Air Quality Index Dashboard")

st.write(
    "A comprehensive analysis of air pollution across "
    "483 monitoring stations, 240 cities and 20 Indian states "
    "from 2009 to 2024. Data sourced from CPCB of India."
)


# --------------------------------------------------
# Dashboard metrics
# --------------------------------------------------

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Monitoring Stations", "483")
k2.metric("Cities Covered", "240")
k3.metric("Indian States", "20")
k4.metric("Daily Readings", "7,38,097")
k5.metric("Data Coverage", "15 Yrs")


# --------------------------------------------------
# AQI Scale
# --------------------------------------------------

st.subheader("📊 AQI Scale Reference")

aqi_scale = [
    ("0–50", "🟢 Good", "Safe for everyone."),
    ("51–100", "🟡 Satisfactory", "Minor discomfort for sensitive groups."),
    ("101–200", "🟡 Moderate", "Breathing discomfort on exertion."),
    ("201–300", "🟠 Poor", "Breathing discomfort for most."),
    ("301–400", "🔴 Very Poor", "Respiratory illness on exposure."),
    ("401–500", "🟤 Severe", "Dangerous even on light activity.")
]

cols = st.columns(6)

for col, (aqi_range, category, description) in zip(cols, aqi_scale):
    with col:
        st.metric(category, aqi_range)
        st.caption(description)


# --------------------------------------------------
# India AQI Map
# --------------------------------------------------

st.subheader("🗺️ India AQI Heat Map")

st.caption(
    "Hover over any point to see the city, state and AQI."
)

map_df = df.dropna(
    subset=["latitude", "longitude", "AQI"]
)

map_df = (
    map_df
    .groupby(
        [
            "station_code",
            "city",
            "state",
            "latitude",
            "longitude"
        ]
    )["AQI"]
    .mean()
    .reset_index()
)

fig_map = px.scatter_map(
    map_df,
    lat="latitude",
    lon="longitude",
    color="AQI",
    size="AQI",
    size_max=18,
    hover_name="city",
    hover_data={
        "state": True,
        "AQI": ":.0f",
        "latitude": False,
        "longitude": False
    },
    color_continuous_scale=[
        [0, "#2DC653"],
        [0.2, "#A8E063"],
        [0.4, "#F9C74F"],
        [0.6, "#F4A261"],
        [0.8, "#E63946"],
        [1, "#6C1515"]
    ],
    range_color=[50, 200],
    map_style="open-street-map",
    zoom=4,
    center={
        "lat": 22.5,
        "lon": 82.0
    },
    height=520
)

fig_map.update_layout(
    paper_bgcolor=t["CARD"],
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(
    fig_map,
    use_container_width=True
)


# --------------------------------------------------
# National AQI Trend
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("📈 National AQI Trend")

    yearly = (
        df.groupby("year")["AQI"]
        .mean()
        .reset_index()
    )

    fig1 = px.line(
        yearly,
        x="year",
        y="AQI",
        markers=True,
        color_discrete_sequence=[t["ACCENT"]],
        title="India Average AQI"
    )

    fig1.add_vrect(
        x0=2019.8,
        x1=2020.8,
        fillcolor="rgba(45,198,83,0.12)",
        line_width=0,
        annotation_text="COVID 2020",
        annotation_font_color="#2DC653"
    )

    fig1.update_traces(
        line_width=2.5,
        marker_size=7
    )

    fig1.update_layout(**CL)

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# --------------------------------------------------
# AQI Category Distribution
# --------------------------------------------------

with col2:

    st.subheader("🥧 AQI Category Share")

    bucket_counts = (
        df["AQI_Bucket"]
        .value_counts()
        .reindex(BUCKET_ORDER)
        .dropna()
    )

    fig2 = go.Figure(
        go.Pie(
            labels=bucket_counts.index,
            values=bucket_counts.values,
            marker=dict(
                colors=[
                    aqi_bucket_color(bucket)
                    for bucket in bucket_counts.index
                ]
            ),
            hole=0.45,
            textinfo="label+percent"
        )
    )

    fig2.update_layout(
        **CL,
        showlegend=False,
        title="AQI Category Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# --------------------------------------------------
# City Analysis
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.subheader("🔴 Top 5 Most Polluted Cities")

    polluted = (
        df.groupby("city")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )

    for city, aqi in polluted.items():
        st.write(
            f"🏙️ **{city}** — AQI **{aqi:.0f}**"
        )


with col2:

    st.subheader("🟢 Top 5 Cleanest Cities")

    cleanest = (
        df.groupby("city")["AQI"]
        .mean()
        .sort_values()
        .head(5)
    )

    for city, aqi in cleanest.items():
        st.write(
            f"🌿 **{city}** — AQI **{aqi:.0f}**"
        )


# --------------------------------------------------
# Key Facts
# --------------------------------------------------

st.subheader("💡 Did You Know?")

facts = [
    "🗓️ Only 6.3% of days in India have Good air quality over the last 15 years.",
    "🏙️ Delhi NCT's AQI of 161 is 4x worse than Aizawl — India's cleanest city at AQI 47.",
    "🌧️ Monsoon months (Jul–Aug) reduce AQI by nearly 50% compared to winter months.",
    "😷 COVID-19 lockdown in 2020 reduced India's average AQI by 15% in just 2 months.",
    "🌾 Punjab's November AQI spikes to 179 due to paddy stubble burning every harvest season.",
    "📉 NO2 levels have declined by 44% over 15 years thanks to cleaner fuel norms."
]

cols = st.columns(3)

for i, fact in enumerate(facts):

    with cols[i % 3]:
        st.info(fact)


# --------------------------------------------------
# Footer
# --------------------------------------------------

render_footer(t)
