import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Analisis Timbulan Sampah - Kutai Kartanegara",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "hasil_final_with_clusters.csv"
)


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    # Tipe data
    df["Cluster"] = df["Cluster"].astype(int)
    df["Kategori"] = df["Kategori"].astype(str)

    numeric_columns = [
        "Penduduk_2023",
        "Timbulan_2023",
        "Penduduk_2024",
        "Timbulan_2024"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


df = load_data()


# =========================================================
# HEADER
# =========================================================

st.title("Analisis Timbulan Sampah")

st.subheader(
    "Kabupaten Kutai Kartanegara | 2023–2024"
)

st.write(
    "Dashboard interaktif hasil pengelompokan kecamatan "
    "berdasarkan jumlah penduduk dan timbulan sampah "
    "menggunakan metode K-Medoids."
)

st.divider()


# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.header("Filter")

year = st.sidebar.selectbox(
    "Tahun",
    [2023, 2024],
    index=1
)

categories = [
    "Semua"
] + sorted(
    df["Kategori"].unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Kategori Cluster",
    categories
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if selected_category != "Semua":

    filtered_df = filtered_df[
        filtered_df["Kategori"] == selected_category
    ]


population_column = f"Penduduk_{year}"
waste_column = f"Timbulan_{year}"


# =========================================================
# KPI
# =========================================================

total_kecamatan = len(filtered_df)

total_population = filtered_df[
    population_column
].sum()

total_waste = filtered_df[
    waste_column
].sum()

total_clusters = filtered_df[
    "Cluster"
].nunique()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Jumlah Kecamatan",
        f"{total_kecamatan}"
    )


with col2:

    st.metric(
        "Total Penduduk",
        f"{total_population:,.0f}"
    )


with col3:

    st.metric(
        "Total Timbulan Sampah",
        f"{total_waste:,.2f}"
    )


with col4:

    st.metric(
        "Jumlah Cluster",
        f"{total_clusters}"
    )


st.divider()


# =========================================================
# SCATTER PLOT
# =========================================================

left_column, right_column = st.columns(2)


with left_column:

    st.subheader(
        f"Penduduk vs Timbulan Sampah ({year})"
    )

    fig_scatter = px.scatter(
        filtered_df,
        x=population_column,
        y=waste_column,
        color="Kategori",
        hover_name="Kecamatan",
        hover_data={
            population_column: ":,.0f",
            waste_column: ":,.2f",
            "Cluster": True
        },
        labels={
            population_column: "Jumlah Penduduk",
            waste_column: "Timbulan Sampah",
            "Kategori": "Kategori"
        }
    )

    fig_scatter.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


# =========================================================
# BAR CHART
# =========================================================

with right_column:

    st.subheader(
        f"Timbulan Sampah per Kecamatan ({year})"
    )

    chart_df = filtered_df.sort_values(
        waste_column,
        ascending=True
    )

    fig_bar = px.bar(
        chart_df,
        x=waste_column,
        y="Kecamatan",
        orientation="h",
        color="Kategori",
        labels={
            waste_column: "Timbulan Sampah",
            "Kecamatan": "Kecamatan",
            "Kategori": "Kategori"
        },
        hover_data={
            waste_column: ":,.2f"
        }
    )

    fig_bar.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )


# =========================================================
# CLUSTER DISTRIBUTION
# =========================================================

st.subheader(
    "Distribusi Kecamatan per Cluster"
)

cluster_df = (
    filtered_df
    .groupby(
        ["Cluster", "Kategori"]
    )
    .size()
    .reset_index(
        name="Jumlah Kecamatan"
    )
    .sort_values("Cluster")
)


fig_cluster = px.bar(
    cluster_df,
    x="Kategori",
    y="Jumlah Kecamatan",
    color="Kategori",
    text="Jumlah Kecamatan",
    labels={
        "Kategori": "Kategori Cluster",
        "Jumlah Kecamatan": "Jumlah Kecamatan"
    }
)

fig_cluster.update_traces(
    textposition="outside"
)

fig_cluster.update_layout(
    showlegend=False,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)

st.plotly_chart(
    fig_cluster,
    use_container_width=True
)


# =========================================================
# DATA TABLE
# =========================================================

st.subheader(
    f"Data Kecamatan ({year})"
)

display_df = filtered_df[
    [
        "Kecamatan",
        "Cluster",
        "Kategori",
        population_column,
        waste_column
    ]
].copy()


display_df = display_df.sort_values(
    waste_column,
    ascending=False
)


display_df = display_df.rename(
    columns={
        population_column: "Penduduk",
        waste_column: "Timbulan Sampah"
    }
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.caption(
    "Sumber data: hasil pengolahan dataset penelitian. "
    "Hasil clustering telah dihitung sebelumnya menggunakan "
    "metode K-Medoids."
)