import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data_loader import load_all_data
from Theme import (
    get_theme,
    inject_theme_css,
    get_chart_layout,
    render_sidebar,
    render_footer,
    MONTHS,
    bar_color_from_aqi
)

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Station Analysis — India AQI",
    page_icon="📡",
    layout="wide"
)

t = get_theme()
inject_theme_css(t)
CL = get_chart_layout(t)

year_range = render_sidebar(t)

# --------------------------------------------------
# Load data
# --------------------------------------------------

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()

df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# --------------------------------------------------
# Page title
# --------------------------------------------------

st.title("📡 Station Analysis")
st.caption("Detailed analysis of individual air-quality monitoring stations.")

# --------------------------------------------------
# Summary
# --------------------------------------------------

station_avg = df.groupby("station_code")["AQI"].mean()

worst_aqi = station_avg.max()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Monitoring Stations",
    df["station_code"].nunique()
)

c2.metric(
    "Cities Covered",
    df["city"].nunique()
)

c3.metric(
    "States Covered",
    df["state"].nunique()
)

c4.metric(
    "Highest Station AQI",
    f"{worst_aqi:.0f}"
)

st.divider()

# --------------------------------------------------
# Top 15 polluted stations
# --------------------------------------------------

st.header("🔴 Top 15 Most Polluted Stations")

stn_aqi = (
    df.groupby("station_code")["AQI"]
    .mean()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

station_info = df[
    ["station_code", "city", "state"]
].drop_duplicates("station_code")

stn_aqi = stn_aqi.merge(
    station_info,
    on="station_code",
    how="left"
)

stn_aqi["label"] = (
    stn_aqi["station_code"]
    + " — "
    + stn_aqi["city"].fillna("Unknown")
    + " ("
    + stn_aqi["state"].fillna("")
    + ")"
)

fig1 = go.Figure(
    go.Bar(
        x=stn_aqi["AQI"].round(0),
        y=stn_aqi["label"],
        orientation="h",
        marker_color=[
            "#E63946" if x > 170
            else "#F4A261" if x > 150
            else "#F9C74F"
            for x in stn_aqi["AQI"]
        ],
        text=stn_aqi["AQI"].round(0),
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Average AQI: %{x:.0f}<extra></extra>"
    )
)

fig1.update_layout(
    **CL,
    title="Top 15 Most Polluted Monitoring Stations",
    height=520,
    xaxis_title="Average AQI",
    yaxis_title=""
)

fig1.update_yaxes(autorange="reversed")

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# Top 10 cleanest stations
# --------------------------------------------------

st.header("🟢 Top 10 Cleanest Stations")

clean_stn = (
    df.groupby("station_code")["AQI"]
    .mean()
    .sort_values()
    .head(10)
    .reset_index()
)

clean_stn = clean_stn.merge(
    station_info,
    on="station_code",
    how="left"
)

clean_stn["label"] = (
    clean_stn["station_code"]
    + " — "
    + clean_stn["city"].fillna("Unknown")
    + " ("
    + clean_stn["state"].fillna("")
    + ")"
)

fig2 = go.Figure(
    go.Bar(
        x=clean_stn["AQI"].round(0),
        y=clean_stn["label"],
        orientation="h",
        marker_color=[
            "#2DC653" if x <= 50
            else "#A8E063" if x <= 75
            else "#F9C74F"
            for x in clean_stn["AQI"]
        ],
        text=clean_stn["AQI"].round(0),
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Average AQI: %{x:.0f}<extra></extra>"
    )
)

fig2.update_layout(
    **CL,
    title="Top 10 Cleanest Monitoring Stations",
    height=420,
    xaxis_title="Average AQI",
    yaxis_title=""
)

fig2.update_yaxes(autorange="reversed")

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --------------------------------------------------
# AQI variation within a city
# --------------------------------------------------

st.header("🏙️ AQI Variation Within a City")

city_station_count = (
    df.groupby("city")["station_code"]
    .nunique()
)

multi_station_cities = sorted(
    city_station_count[
        city_station_count > 1
    ].index.tolist()
)

if multi_station_cities:

    default_city = (
        "Delhi"
        if "Delhi" in multi_station_cities
        else multi_station_cities[0]
    )

    selected_city = st.selectbox(
        "Select City",
        multi_station_cities,
        index=multi_station_cities.index(default_city)
    )

    city_stations = (
        df[df["city"] == selected_city]
        .groupby("station_code")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig3 = go.Figure(
        go.Bar(
            x=city_stations["AQI"].round(0),
            y=city_stations["station_code"],
            orientation="h",
            marker_color=[
                bar_color_from_aqi(a)
                for a in city_stations["AQI"]
            ],
            text=city_stations["AQI"].round(0),
            textposition="inside",
            hovertemplate=(
                "<b>Station: %{y}</b>"
                "<br>Average AQI: %{x:.0f}"
                "<extra></extra>"
            )
        )
    )

    fig3.update_layout(
        **CL,
        title=f"AQI Variation Across Stations in {selected_city}",
        height=max(300, len(city_stations) * 40),
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig3.update_yaxes(autorange="reversed")

    st.plotly_chart(fig3, use_container_width=True)

    maximum = city_stations["AQI"].max()
    minimum = city_stations["AQI"].min()
    gap = maximum - minimum

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Highest Station AQI",
        f"{maximum:.0f}"
    )

    c2.metric(
        "Lowest Station AQI",
        f"{minimum:.0f}"
    )

    c3.metric(
        "AQI Difference",
        f"{gap:.0f}"
    )

else:
    st.info("No city has multiple monitoring stations in the selected data.")

# --------------------------------------------------
# Station trend explorer
# --------------------------------------------------

st.header("📈 Station AQI Trend Explorer")

all_stations = sorted(
    df["station_code"].dropna().unique()
)

if all_stations:

    default_station = (
        "PB03"
        if "PB03" in all_stations
        else all_stations[0]
    )

    selected_station = st.selectbox(
        "Select Station",
        all_stations,
        index=all_stations.index(default_station)
    )

    station_df = df[
        df["station_code"] == selected_station
    ]

    station_city = (
        station_df["city"].mode().iloc[0]
        if not station_df["city"].mode().empty
        else "Unknown"
    )

    station_state = (
        station_df["state"].mode().iloc[0]
        if not station_df["state"].mode().empty
        else "Unknown"
    )

    station_yearly = (
        station_df.groupby("year")["AQI"]
        .mean()
        .reset_index()
    )

    station_monthly = (
        station_df.groupby("month")["AQI"]
        .mean()
        .reset_index()
    )

    station_monthly["month_name"] = (
        station_monthly["month"]
        .apply(lambda x: MONTHS[x - 1])
    )

    st.write(
        f"**Station:** {selected_station}  |  "
        f"**City:** {station_city}  |  "
        f"**State:** {station_state}  |  "
        f"**Average AQI:** {station_df['AQI'].mean():.0f}"
    )

    col1, col2 = st.columns(2)

    with col1:

        national_avg = (
            df.groupby("year")["AQI"]
            .mean()
            .reset_index()
        )

        fig4 = go.Figure()

        fig4.add_trace(
            go.Scatter(
                x=station_yearly["year"],
                y=station_yearly["AQI"],
                name=selected_station,
                mode="lines+markers",
                line=dict(
                    color=t["ACCENT"],
                    width=3
                )
            )
        )

        fig4.add_trace(
            go.Scatter(
                x=national_avg["year"],
                y=national_avg["AQI"],
                name="National Average",
                mode="lines",
                line=dict(
                    color="#F9C74F",
                    width=2,
                    dash="dot"
                )
            )
        )

        fig4.update_layout(
            **CL,
            title=f"{selected_station} — Yearly AQI",
            height=340,
            xaxis_title="Year",
            yaxis_title="Average AQI"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    with col2:

        fig5 = go.Figure(
            go.Bar(
                x=station_monthly["month_name"],
                y=station_monthly["AQI"],
                marker_color=[
                    bar_color_from_aqi(a)
                    for a in station_monthly["AQI"]
                ],
                text=station_monthly["AQI"].round(0),
                textposition="outside"
            )
        )

        fig5.update_layout(
            **CL,
            title=f"{selected_station} — Monthly AQI",
            height=340,
            xaxis_title="Month",
            yaxis_title="Average AQI"
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

# --------------------------------------------------
# Stations in selected state
# --------------------------------------------------

st.header("🗺️ All Stations in a State")

states = sorted(
    df["state"].dropna().unique()
)

if states:

    default_state = (
        "Punjab"
        if "Punjab" in states
        else states[0]
    )

    selected_state = st.selectbox(
        "Select State",
        states,
        index=states.index(default_state)
    )

    state_stations = (
        df[df["state"] == selected_state]
        .groupby("station_code")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    state_station_info = df[
        ["station_code", "city"]
    ].drop_duplicates("station_code")

    state_stations = state_stations.merge(
        state_station_info,
        on="station_code",
        how="left"
    )

    state_stations["label"] = (
        state_stations["station_code"]
        + " — "
        + state_stations["city"].fillna("Unknown")
    )

    fig6 = go.Figure(
        go.Bar(
            x=state_stations["AQI"].round(0),
            y=state_stations["label"],
            orientation="h",
            marker_color=[
                bar_color_from_aqi(a)
                for a in state_stations["AQI"]
            ],
            text=state_stations["AQI"].round(0),
            textposition="inside",
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Average AQI: %{x:.0f}"
                "<extra></extra>"
            )
        )
    )

    fig6.update_layout(
        **CL,
        title=f"Stations in {selected_state} — AQI",
        height=max(300, len(state_stations) * 50),
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig6.update_yaxes(autorange="reversed")

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------

render_footer(t)
