import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nissan Automotive Benchmark Dashboard",
    layout="wide"
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("nissan_dataset.csv")
    df["year"] = df["year"].astype(int)
    df["ex_showroom_price"] = df["ex_showroom_price"].astype(float)
    df["quoted_price"] = df["quoted_price"].astype(float)
    return df


df = load_data()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("Nissan Automotive Intelligence")
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Select page",
    [
        "Dashboard",
        "Model Comparison",
        "Pricing Trends",
        "Feature Benchmarking",
        "Dealer Quotations",
        "Settings",
    ],
    index=0,
)

with st.sidebar.expander("Filters", expanded=True):
    market = st.selectbox("Market", ["All"] + sorted(df["market"].unique().tolist()))
    model = st.selectbox("Model", ["All"] + sorted(df["model"].unique().tolist()))
    year = st.selectbox("Year", ["All"] + sorted(df["year"].unique().tolist()))

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h2>Automotive Benchmark Dashboard</h2>", unsafe_allow_html=True)
st.caption("User: DZ1")

st.success("This dashboard provides a unified view of Nissan’s model hierarchy, pricing, features, and competitive positioning across markets.")

# ---------------------------------------------------------
# FILTERING
# ---------------------------------------------------------
filtered = df.copy()

if market != "All":
    filtered = filtered[filtered["market"] == market]

if model != "All":
    filtered = filtered[filtered["model"] == model]

if year != "All":
    filtered = filtered[filtered["year"] == year]

if page == "Dashboard":
    # ---------------------------------------------------------
    # KPI CARDS
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Unique Models", filtered["model"].nunique())
    col2.metric("Unique Trims", filtered["trim"].nunique())
    col3.metric("Avg Ex-Showroom Price", f"${filtered['ex_showroom_price'].mean():,.0f}")
    col4.metric("Avg Discount", f"${filtered['discount_offer'].mean():,.0f}")

    # ---------------------------------------------------------
    # PRICING TREND CHART
    # ---------------------------------------------------------
    st.markdown("### Historical Pricing Trends")

    price_trend = (
        filtered.groupby(["year", "model"])["ex_showroom_price"]
        .mean()
        .reset_index()
    )

    if not price_trend.empty:
        fig_price = px.line(
            price_trend,
            x="year",
            y="ex_showroom_price",
            color="model",
            markers=True,
            title="Yearly Price Movement by Model"
        )
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No pricing data available for selected filters.")

    # ---------------------------------------------------------
    # FEATURE BENCHMARKING
    # ---------------------------------------------------------
    st.markdown("### Feature Benchmarking")

    feature_cols = ["infotainment_size_inch", "ADAS_level", "airbags", "safety_rating"]
    feature_data = (
        filtered.groupby("model")[feature_cols]
        .mean()
        .reset_index()
    )

    if not feature_data.empty:
        fig_feat = px.bar(
            feature_data,
            x="model",
            y="infotainment_size_inch",
            title="Infotainment Size Comparison",
            color="model"
        )
        st.plotly_chart(fig_feat, use_container_width=True)
    else:
        st.info("No feature data available.")

    # ---------------------------------------------------------
    # COMPETITOR POSITIONING
    # ---------------------------------------------------------
    st.markdown("### Competitor Positioning Score")

    pos_data = (
        filtered.groupby("model")["positioning_score"]
        .mean()
        .reset_index()
    )

    if not pos_data.empty:
        fig_pos = px.bar(
            pos_data,
            x="model",
            y="positioning_score",
            title="Positioning Score by Model",
            color="model"
        )
        st.plotly_chart(fig_pos, use_container_width=True)
    else:
        st.info("No positioning data available.")

    # ---------------------------------------------------------
    # MYSTERY SHOPPER QUOTATIONS
    # ---------------------------------------------------------
    st.markdown("### Mystery Shopper Quotation Insights")

    quote_data = (
        filtered.groupby("model")[['quoted_price']]
        .mean()
        .reset_index()
    )

    if not quote_data.empty:
        fig_quote = px.bar(
            quote_data,
            x="model",
            y="quoted_price",
            title="Average Quoted Price by Model",
            color="model"
        )
        st.plotly_chart(fig_quote, use_container_width=True)
    else:
        st.info("No quotation data available.")

    # ---------------------------------------------------------
    # RAW DATA
    # ---------------------------------------------------------
    with st.expander("View Raw Data"):
        st.dataframe(filtered, use_container_width=True)

elif page == "Model Comparison":
    st.markdown("<h2>Model Comparison</h2>", unsafe_allow_html=True)
    st.write("Compare models across key metrics using filtered data.")

    comp_data = (
        filtered.groupby("model")[['ex_showroom_price', 'quoted_price', 'discount_offer', 'positioning_score']]
        .mean()
        .reset_index()
        .sort_values('ex_showroom_price')
    )
    st.dataframe(comp_data, use_container_width=True)

elif page == "Pricing Trends":
    st.markdown("<h2>Pricing Trends</h2>", unsafe_allow_html=True)
    st.write("View price movement trends for the selected filters.")

    price_trend = (
        filtered.groupby(["year", "model"])["ex_showroom_price"]
        .mean()
        .reset_index()
    )
    if not price_trend.empty:
        fig_price = px.line(
            price_trend,
            x="year",
            y="ex_showroom_price",
            color="model",
            markers=True,
            title="Yearly Price Movement by Model"
        )
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No pricing data available for selected filters.")

elif page == "Feature Benchmarking":
    st.markdown("<h2>Feature Benchmarking</h2>", unsafe_allow_html=True)
    st.write("Compare feature scores and safety attributes across models.")

    feature_cols = ["infotainment_size_inch", "ADAS_level", "airbags", "safety_rating"]
    feature_data = (
        filtered.groupby("model")[feature_cols]
        .mean()
        .reset_index()
    )

    if not feature_data.empty:
        fig_feat = px.bar(
            feature_data,
            x="model",
            y="infotainment_size_inch",
            title="Infotainment Size Comparison",
            color="model"
        )
        st.plotly_chart(fig_feat, use_container_width=True)

        st.markdown("### Safety and ADAS Benchmark")
        fig_safety = px.bar(
            feature_data,
            x="model",
            y=["ADAS_level", "airbags", "safety_rating"],
            barmode="group",
            title="Safety and ADAS Benchmark"
        )
        st.plotly_chart(fig_safety, use_container_width=True)
    else:
        st.info("No feature data available.")

elif page == "Dealer Quotations":
    st.markdown("<h2>Dealer Quotations</h2>", unsafe_allow_html=True)
    st.write("Review dealer quoted prices for the selected filters.")

    quote_data = (
        filtered.groupby("model")[['quoted_price']]
        .mean()
        .reset_index()
    )
    if not quote_data.empty:
        fig_quote = px.bar(
            quote_data,
            x="model",
            y="quoted_price",
            title="Average Quoted Price by Model",
            color="model"
        )
        st.plotly_chart(fig_quote, use_container_width=True)
        st.dataframe(quote_data, use_container_width=True)
    else:
        st.info("No quotation data available.")

elif page == "Settings":
    st.markdown("<h2>Settings</h2>", unsafe_allow_html=True)
    st.info("Use the sidebar filters and navigation menu to adjust the dashboard view.")
    st.write("This page can be extended with export, refresh, or data source controls.")


#Run like this: .venv/bin/python -m streamlit run dashboard.py
