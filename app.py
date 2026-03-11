import streamlit as st
from streamlit_option_menu import option_menu

# Import page render functions
from pages.home import render_home

st.set_page_config(
    page_title="Biodiversity Insights",
    page_icon="🌿",
    layout="wide",
)

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Biodiversity Insights",
        options=["Home", "Overview", "Data", "About"],
        icons=["house", "bar-chart", "database", "info-circle"],
        menu_icon="leaf",
        default_index=0,
    )

# ----- PAGE ROUTING -----

if selected == "Home":
    render_home()

elif selected == "Overview":
    st.title("📊 Overview")
    st.write("Overview page placeholder")

elif selected == "Data":
    st.title("Data")

    from src.db import init_db, load_csv_folder, get_conn

    init_db()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Load / refresh CSVs into DuckDB"):
            created = load_csv_folder("data")
            st.success(f"Loaded {len(created)} tables")
            st.write(created)

    with col2:
        with get_conn(read_only=True) as con:
            tables = con.execute("SHOW TABLES").fetchall()
        st.write("Tables in DB:")
        st.write([t[0] for t in tables])

    table_names = [t[0] for t in tables]
    if table_names:
        chosen = st.selectbox("Preview table", table_names)
        with get_conn(read_only=True) as con:
            df_preview = con.execute(f"SELECT * FROM {chosen} LIMIT 50").df()
        st.dataframe(df_preview, use_container_width=True)

elif selected == "About":
    st.title("ℹ️ About")
    st.write("About page placeholder")
