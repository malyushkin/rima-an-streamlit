import streamlit as st
import pandas as pd
import gdown

st.title("Censorship Index: Article Analysis")

# Если файл уже лежит локально — нет смысла вызывать gdown.
# Оставляйте gdown только, если планируете скачивать что-то из интернета.
# url = "https://drive.google.com/uc?id=1-GpHnMqaciU9Pr3sEwIRPP_Bo8JS9_fq"
output = "compressed_gzip.parquet"
# gdown.download(url, output, quiet=False)

@st.cache_data
def load_data():
    # Читаем Parquet-файл. Pandas автоматически распознает, чем он сжат (gzip, snappy, zstd и т.д.).
    df = pd.read_parquet(output)

    # Убедитесь, что в df.columns действительно есть "published_dt" и "source_slug".
    # Если нет, код ниже упадёт с ошибкой.
    return df

df = load_data()

# Преобразуем published_dt в datetime.
# Если в файле нет колонки "published_dt", вы получите ошибку KeyError.
df["published_dt"] = pd.to_datetime(df["published_dt"], errors="coerce")

st.write(f"### Dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# Фильтр по источникам: "source_slug" должна существовать в колонках df.
source_filter = st.multiselect("Filter by Source", df["source_slug"].dropna().unique())

# Если в published_dt есть валидные даты, найдём min и max.
min_date = df["published_dt"].min().date()
max_date = df["published_dt"].max().date()

date_range = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Фильтрация по выбранным датам
filtered_df = df[
    (df["published_dt"] >= pd.to_datetime(date_range[0])) &
    (df["published_dt"] <= pd.to_datetime(date_range[1]))
]

# Фильтр по источникам, если выбраны значения
if source_filter:
    filtered_df = filtered_df[filtered_df["source_slug"].isin(source_filter)]

# Показываем первые 1000 строк таблицы
st.dataframe(filtered_df.head(1000))
#
# # Считаем, сколько статей в каждом месяце
# st.subheader("Article Count Over Time")
# articles_per_month = filtered_df.groupby(
#     filtered_df["published_dt"].dt.to_period("M")
# ).size()
#
# # Рисуем линейный график
# st.line_chart(articles_per_month)
#
# # Даём кнопку для скачивания отфильтрованных данных в CSV
# st.download_button(
#     "Download Filtered Data",
#     filtered_df.to_csv(index=False),
#     "filtered_data.csv",
#     "text/csv",
# )