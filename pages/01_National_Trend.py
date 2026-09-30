import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
    page_title="National Trend — India AQI",
    page_icon="📈",
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

st.title("📈 National AQI Trend")

st.write(
    f"Tracking India's air quality from "
    f"{year_range[0]} to {year_range[1]} "
    f"across monitoring stations."
)

st.divider()


# --------------------------------------------------
# Chart 1 — Yearly AQI Trend
# --------------------------------------------------

st.subheader("📉 India Average AQI — Year by Year")

yearly = (
    df.groupby("year")["AQI"]
    .mean()
    .reset_index()
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["AQI"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=(
            "rgba(0,212,255,0.08)"
            if t["is_dark"]
            else "rgba(0,119,182,0.08)"
        ),
        line=dict(
            color=t["ACCENT"],
            width=3
        ),
        marker=dict(
            size=8,
            color=t["ACCENT"]
        ),
        hovertemplate=(
            "<b>Year:</b> %{x}<br>"
            "<b>Average AQI:</b> %{y:.1f}"
            "<extra></extra>"
        )
    )
)

# COVID year marker
if 2020 in yearly["year"].values:
    fig1.add_vrect(
        x0=2019.8,
        x1=2020.8,
        fillcolor="rgba(45,198,83,0.12)",
        line_width=0,
        annotation_text="2020",
        annotation_position="top left"
    )

# Peak AQI
peak_row = yearly.loc[yearly["AQI"].idxmax()]

fig1.add_annotation(
    x=peak_row["year"],
    y=peak_row["AQI"],
    text=f"Peak: {peak_row['AQI']:.0f}",
    showarrow=True,
    arrowhead=2,
    arrowcolor="#E63946",
    font=dict(
        color="#E63946"
    )
)

fig1.update_layout(
    **CL,
    height=400,
    xaxis_title="Year",
    yaxis_title="Average AQI",
    showlegend=False,
    title="India National Average AQI"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.info(
    f"📊 Highest average AQI in the selected period: "
    f"{peak_row['AQI']:.1f} in {int(peak_row['year'])}."
)


# --------------------------------------------------
# Chart 2 — AQI Distribution
# --------------------------------------------------

st.subheader("📦 AQI Distribution Per Year")

fig2 = px.box(
    df,
    x="year",
    y="AQI",
    color_discrete_sequence=[t["ACCENT"]],
    title="Year-wise AQI Distribution"
)

fig2.update_layout(
    **CL,
    height=420,
    xaxis_title="Year",
    yaxis_title="AQI"
)

fig2.update_traces(
    marker_color=t["ACCENT"],
    line_color=t["ACCENT"],
    fillcolor=(
        "rgba(0,212,255,0.15)"
        if t["is_dark"]
        else "rgba(0,119,182,0.15)"
    ),
    marker_outliercolor="#E63946"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# --------------------------------------------------
# Chart 3 — Year × Month Heatmap
# --------------------------------------------------

st.subheader("🔥 Year × Month AQI Heatmap")

pivot = (
    df.pivot_table(
        values="AQI",
        index="year",
        columns="month",
        aggfunc="mean"
    )
    .reindex(columns=range(1, 13))
)

fig3 = go.Figure(
    data=go.Heatmap(
        z=pivot.values,
        x=MONTHS,
        y=pivot.index,
        colorscale=[
            [0, "#2DC653"],
            [0.3, "#F9C74F"],
            [0.6, "#F4A261"],
            [0.8, "#E63946"],
            [1, "#6C1515"]
        ],
        hovertemplate=(
            "<b>Year:</b> %{y}<br>"
            "<b>Month:</b> %{x}<br>"
            "<b>AQI:</b> %{z:.0f}"
            "<extra></extra>"
        ),
        colorbar=dict(
            title="AQI"
        )
    )
)

fig3.update_layout(
    **CL,
    height=520,
    title="AQI Heatmap — Year × Month",
    xaxis_title="Month",
    yaxis_title="Year"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# Chart 4 — COVID comparison
# --------------------------------------------------

st.subheader("😷 Pre-COVID vs COVID vs Post-COVID")

df["era"] = pd.cut(
    df["year"],
    bins=[2008, 2019, 2020, 2024],
    labels=[
        "Pre-COVID (2009–2019)",
        "COVID Year (2020)",
        "Post-COVID (2021–2024)"
    ]
)

era_aqi = (
    df.groupby(
        "era",
        observed=True
    )["AQI"]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    era_aqi,
    x="era",
    y="AQI",
    color="era",
    text=era_aqi["AQI"].round(1),
    title="Average AQI Across Three Periods",
    color_discrete_map={
        "Pre-COVID (2009–2019)": "#F4A261",
        "COVID Year (2020)": "#2DC653",
        "Post-COVID (2021–2024)": t["ACCENT"]
    }
)

fig4.update_traces(
    textposition="outside"
)

fig4.update_layout(
    **CL,
    height=380,
    showlegend=False,
    xaxis_title="",
    yaxis_title="Average AQI"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# --------------------------------------------------
# Summary statistics
# --------------------------------------------------

st.subheader("📊 Summary Statistics")

yearly_all = (
    df.groupby("year")["AQI"]
    .mean()
)

worst_year = yearly_all.idxmax()
best_year = yearly_all.idxmin()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Highest Yearly AQI",
    f"{yearly_all.max():.0f}",
    f"{int(worst_year)}"
)

col2.metric(
    "Lowest Yearly AQI",
    f"{yearly_all.min():.0f}",
    f"{int(best_year)}"
)

col3.metric(
    "Overall Average AQI",
    f"{yearly_all.mean():.0f}"
)

if len(yearly_all) > 1:
    change = yearly_all.iloc[-1] - yearly_all.iloc[0]

    col4.metric(
        "AQI Change",
        f"{change:+.0f}",
        f"{int(yearly_all.index[0])} → {int(yearly_all.index[-1])}"
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

render_footer(t)
