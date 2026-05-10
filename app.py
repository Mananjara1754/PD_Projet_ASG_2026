import streamlit as st
import lot1
import lot2
import lot3

st.set_page_config(page_title="Pipeline Assemblage", layout="wide")

st.sidebar.title("Pipeline d'Assemblage De Novo")
page = st.sidebar.radio("Navigation", ["Lot 1 : Ingestion & Qualité", "Lot 2 : Alignement", "Lot 3 : Assemblage"])

if page == "Lot 1 : Ingestion & Qualité":
    lot1.run()
elif page == "Lot 2 : Alignement":
    lot2.run()
elif page == "Lot 3 : Assemblage":
    lot3.run()
