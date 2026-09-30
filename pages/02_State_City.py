import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_loader import load_all_data
from Theme import (
    get_theme,
    get_chart_layout,
    render_sidebar,
    render_footer,
    MONTHS
)


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="State & City — India AQI",
    page_icon="🗺️",
    layout="wide"
)

t = get_theme()
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

st.title("🗺️ State & City Analysis")

st.write(
    "Compare air quality across Indian states and cities "
    "using AQI data."
)

st.divider()


# ==================================================
# STATE ANALYSIS
# ==================================================

st.subheader("🏛️ State-wise AQI Comparison")

col1, col2 = st.columns(2)


# --------------------------------------------------
# Top 10 polluted states
# --------------------------------------------------

with col1:

    state_aqi = (
        df.groupby("state")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig1 = px.bar(
        state_aqi,
        x="AQI",
        y="state",
        orientation="h",
        color="AQI",
        color_continuous_scale=[
            "#F9C74F",
            "#F4A261",
            "#E63946"
        ],
        text=state_aqi["AQI"].round(0),
        title="🔴 Top 10 States by Average AQI"
    )

    fig1.update_traces(
        textposition="inside"
    )

    fig1.update_layout(
        **CL,
        height=420,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig1.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# --------------------------------------------------
# All states
# --------------------------------------------------

with col2:

    all_states = (
        df.groupby("state")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig2 = px.bar(
        all_states,
        x="AQI",
        y="state",
        orientation="h",
        color="AQI",
        color_continuous_scale=[
            [0, "#2DC653"],
            [0.4, "#F9C74F"],
            [0.7, "#F4A261"],
            [1, "#E63946"]
        ],
        text=all_states["AQI"].round(0),
        title="🗺️ All States — Average AQI"
    )

    fig2.update_traces(
        textposition="inside"
    )

    fig2.update_layout(
        **CL,
        height=520,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig2.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ==================================================
# STATE TREND
# ==================================================

st.subheader("📈 State AQI Trend Explorer")

all_states_list = sorted(
    df["state"]
    .dropna()
    .unique()
    .tolist()
)

default_state = (
    "Punjab"
    if "Punjab" in all_states_list
    else all_states_list[0]
)

selected_state = st.selectbox(
    "🗺️ Select a State",
    all_states_list,
    index=all_states_list.index(default_state)
)


state_df = df[df["state"] == selected_state]

state_trend = (
    state_df.groupby("year")["AQI"]
    .mean()
    .reset_index()
)

national_trend = (
    df.groupby("year")["AQI"]
    .mean()
    .reset_index()
)


fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=state_trend["year"],
        y=state_trend["AQI"],
        mode="lines+markers",
        line=dict(
            color=t["ACCENT"],
            width=3
        ),
        name=selected_state
    )
)

fig3.add_trace(
    go.Scatter(
        x=national_trend["year"],
        y=national_trend["AQI"],
        mode="lines",
        line=dict(
            color="#F9C74F",
            width=2,
            dash="dot"
        ),
        name="National Average"
    )
)

fig3.update_layout(
    **CL,
    height=380,
    title=f"{selected_state} AQI vs National Average",
    xaxis_title="Year",
    yaxis_title="Average AQI"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# State statistics
# --------------------------------------------------

state_avg = state_trend["AQI"].mean()

state_worst = state_trend["AQI"].max()

state_best = state_trend["AQI"].min()

national_avg = df["AQI"].mean()

state_difference = state_avg - national_avg


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    f"{selected_state} Avg AQI",
    f"{state_avg:.0f}"
)

c2.metric(
    "Highest Year AQI",
    f"{state_worst:.0f}"
)

c3.metric(
    "Lowest Year AQI",
    f"{state_best:.0f}"
)

c4.metric(
    "Difference vs National",
    f"{state_difference:+.0f}"
)


# ==================================================
# CITY ANALYSIS
# ==================================================

st.subheader("🏙️ City-Level Analysis")

col1, col2 = st.columns(2)


# --------------------------------------------------
# Most polluted cities
# --------------------------------------------------

with col1:

    top10 = (
        df.groupby("city")["AQI"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig4 = px.bar(
        top10,
        x="AQI",
        y="city",
        orientation="h",
        color="AQI",
        color_continuous_scale=[
            "#F9C74F",
            "#F4A261",
            "#E63946"
        ],
        text=top10["AQI"].round(0),
        title="🔴 Top 10 Cities by Average AQI"
    )

    fig4.update_traces(
        textposition="inside"
    )

    fig4.update_layout(
        **CL,
        height=420,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig4.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# --------------------------------------------------
# Cleanest cities
# --------------------------------------------------

with col2:

    clean10 = (
        df.groupby("city")["AQI"]
        .mean()
        .sort_values()
        .head(10)
        .reset_index()
    )

    fig5 = px.bar(
        clean10,
        x="AQI",
        y="city",
        orientation="h",
        color="AQI",
        color_continuous_scale=[
            "#2DC653",
            "#A8E063",
            "#F9C74F"
        ],
        text=clean10["AQI"].round(0),
        title="🟢 Top 10 Cities by Lowest AQI"
    )

    fig5.update_traces(
        textposition="inside"
    )

    fig5.update_layout(
        **CL,
        height=420,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Average AQI",
        yaxis_title=""
    )

    fig5.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ==================================================
# CITY EXPLORER
# ==================================================

st.subheader("🔍 City AQI Explorer")

all_cities = sorted(
    df["city"]
    .dropna()
    .unique()
    .tolist()
)

default_city = (
    "Amritsar"
    if "Amritsar" in all_cities
    else all_cities[0]
)

selected_city = st.selectbox(
    "🏙️ Select a City",
    all_cities,
    index=all_cities.index(default_city)
)


city_df = df[df["city"] == selected_city]


# --------------------------------------------------
# City yearly trend
# --------------------------------------------------

city_trend = (
    city_df.groupby("year")["AQI"]
    .mean()
    .reset_index()
)


# --------------------------------------------------
# City monthly AQI
# --------------------------------------------------

city_monthly = (
    city_df.groupby("month")["AQI"]
    .mean()
    .reset_index()
)

city_monthly["month_name"] = city_monthly["month"].apply(
    lambda x: MONTHS[int(x) - 1]
)


col1, col2 = st.columns(2)


# --------------------------------------------------
# City yearly chart
# --------------------------------------------------

with col1:

    fig6 = px.line(
        city_trend,
        x="year",
        y="AQI",
        markers=True,
        color_discrete_sequence=[t["ACCENT"]],
        title=f"{selected_city} — Yearly AQI Trend"
    )

    fig6.update_traces(
        line_width=2.5,
        marker_size=7
    )

    fig6.update_layout(
        **CL,
        height=320,
        xaxis_title="Year",
        yaxis_title="Average AQI"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )


# --------------------------------------------------
# City monthly chart
# --------------------------------------------------

with col2:

    fig7 = px.bar(
        city_monthly,
        x="month_name",
        y="AQI",
        color="AQI",
        color_continuous_scale=[
            "#2DC653",
            "#F9C74F",
            "#E63946"
        ],
        title=f"{selected_city} — Monthly AQI"
    )

    fig7.update_layout(
        **CL,
        height=320,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Month",
        yaxis_title="Average AQI"
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )


# --------------------------------------------------
# City statistics
# --------------------------------------------------

if not city_trend.empty:

    city_avg = city_trend["AQI"].mean()

    worst_month = city_monthly.loc[
        city_monthly["AQI"].idxmax(),
        "month_name"
    ]

    best_month = city_monthly.loc[
        city_monthly["AQI"].idxmin(),
        "month_name"
    ]

    city_vs_national = city_avg - national_avg

else:

    city_avg = 0
    worst_month = "N/A"
    best_month = "N/A"
    city_vs_national = 0


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    f"{selected_city} Avg AQI",
    f"{city_avg:.0f}"
)

c2.metric(
    "Highest AQI Month",
    worst_month
)

c3.metric(
    "Lowest AQI Month",
    best_month
)

c4.metric(
    "Difference vs National",
    f"{city_vs_national:+.0f}"
)


# --------------------------------------------------
# Footer
# --------------------------------------------------

render_footer(t)
