import streamlit as st
import pandas as pd
import gdown

st.title("Censorship Index: Article Analysis")

# Download dataset from Google Drive
url = "https://drive.google.com/uc?id=1-GpHnMqaciU9Pr3sEwIRPP_Bo8JS9_fq"
output = "censorship_data.csv"
gdown.download(url, output, quiet=False)

@st.cache_data
def load_data():
    df = pd.read_csv(output, parse_dates=["published_dt"])
    df.to_parquet("censorship_data.parquet", index=False)
    return df

df = load_data()

df["published_dt"] = pd.to_datetime(df["published_dt"], errors="coerce")

st.write(f"### Dataset: {df.shape[0]} rows, {df.shape[1]} columns")

source_filter = st.multiselect("Filter by Source", df["source_slug"].dropna().unique())

min_date = df["published_dt"].min().date()
max_date = df["published_dt"].max().date()

date_range = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

filtered_df = df[
    (df["published_dt"] >= pd.to_datetime(date_range[0])) &
    (df["published_dt"] <= pd.to_datetime(date_range[1]))
]

if source_filter:
    filtered_df = filtered_df[filtered_df["source_slug"].isin(source_filter)]

st.dataframe(filtered_df.head(1000))
st.subheader("Article Count Over Time")
articles_per_month = filtered_df.groupby(
    filtered_df["published_dt"].dt.to_period("M")
).size()

st.line_chart(articles_per_month)

st.download_button(
    "Download Filtered Data",
    filtered_df.to_csv(index=False),
    "filtered_data.csv",
    "text/csv",
)