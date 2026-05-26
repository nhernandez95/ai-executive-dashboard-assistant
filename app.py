import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AI Executive Dashboard Assistant", layout="wide")
st.title("AI Executive Dashboard Assistant")
st.caption("Upload raw business data and generate KPIs, charts, and executive-ready insights.")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

@st.cache_data
def load_sample():
    return pd.read_csv("data/sample_sales_data.csv")

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = load_sample()
    st.info("Using sample sales data. Upload your own file to test the workflow.")

# Normalize columns
for col in df.columns:
    if "date" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")

numeric_cols = df.select_dtypes(include="number").columns.tolist()
date_cols = df.select_dtypes(include="datetime").columns.tolist()
category_cols = df.select_dtypes(include="object").columns.tolist()

st.subheader("Data Preview")
st.dataframe(df, use_container_width=True)

if "Revenue" in df.columns and "Cost" in df.columns:
    df["Profit"] = df["Revenue"] - df["Cost"]
    revenue = df["Revenue"].sum()
    cost = df["Cost"].sum()
    profit = df["Profit"].sum()
    margin = profit / revenue if revenue else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue", f"${revenue:,.0f}")
    c2.metric("Cost", f"${cost:,.0f}")
    c3.metric("Profit", f"${profit:,.0f}")
    c4.metric("Profit Margin", f"{margin:.1%}")

    if date_cols:
        date_col = date_cols[0]
        trend = df.groupby(pd.Grouper(key=date_col, freq="M"))["Revenue"].sum().reset_index()
        fig = px.line(trend, x=date_col, y="Revenue", markers=True, title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

    if "Region" in df.columns:
        region = df.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
        fig = px.bar(region, x="Region", y="Revenue", title="Revenue by Region")
        st.plotly_chart(fig, use_container_width=True)

    if "Product" in df.columns:
        product = df.groupby("Product", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)
        fig = px.bar(product, x="Product", y="Profit", title="Profit by Product")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("AI-Style Executive Summary")
    top_region = df.groupby("Region")["Revenue"].sum().idxmax() if "Region" in df.columns else "the leading segment"
    top_product = df.groupby("Product")["Profit"].sum().idxmax() if "Product" in df.columns else "the leading product"
    st.write(f"""
    **Executive Insight:** Revenue totaled **${revenue:,.0f}** with an estimated profit of **${profit:,.0f}** and margin of **{margin:.1%}**.
    The strongest revenue contributor was **{top_region}**, while **{top_product}** generated the highest profit impact.

    **Recommended Action:** Prioritize growth campaigns around the highest-margin products, investigate low-profit segments,
    and automate this reporting flow so leadership receives weekly KPI updates without manual spreadsheet work.
    """)
else:
    st.warning("For the full demo, include Revenue and Cost columns or use the sample dataset.")
