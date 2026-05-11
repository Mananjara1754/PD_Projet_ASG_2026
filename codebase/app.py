import streamlit as st
import lot1
import lot2
import lot3

def main():
    st.set_page_config(page_title="Pipeline Assemblage De Novo", layout="wide")

    st.sidebar.title("Navigation - Projet ASG")
    page = st.sidebar.radio("Aller à", [
        "Lot 1 : Ingestion & Qualité", 
        "Lot 2 : Alignement", 
        "Lot 3 : Assemblage (Minia 2)"
    ])

    if page == "Lot 1 : Ingestion & Qualité":
        lot1.render_page()
    elif page == "Lot 2 : Alignement":
        lot2.render_page()
    elif page == "Lot 3 : Assemblage (Minia 2)":
        lot3.render_page()

if __name__ == "__main__":
    main()
