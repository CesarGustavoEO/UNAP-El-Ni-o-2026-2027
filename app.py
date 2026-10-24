"""Aplicación grupal UNAP: navegación entre los tres módulos originales."""
import streamlit as st

pages = [
    st.Page("ml1/app.py", title="ML 1 · Similitud histórica", icon=":material/history:", url_path="similitud-historica"),
    st.Page("ml2/app.py", title="ML 2 · Precipitaciones del Perú", icon=":material/rainy:", url_path="precipitaciones"),
    st.Page("ml3/app.py", title="ML 3 · Pronóstico Niño 3.4", icon=":material/show_chart:", url_path="pronostico"),
]
pg = st.navigation(pages, position="sidebar")
pg.run()
