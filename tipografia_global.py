"""Estilos editoriales compartidos, sin modificar datos ni modelos."""
import streamlit as st

def aplicar_tipografia():
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *,
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
    [data-testid="stSidebar"] *, button, input, label {
        font-family: 'DM Sans', Arial, sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'DM Sans', Arial, sans-serif !important;
        letter-spacing: -0.025em !important;
        color: #172C39;
    }
    [data-testid="stMetricValue"] {font-weight: 600;}
    /* Restaurar iconos Material de Streamlit */
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons,
[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 20px !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    direction: ltr !important;
    font-feature-settings: "liga" !important;
    -webkit-font-feature-settings: "liga" !important;
    -webkit-font-smoothing: antialiased !important;
}
    </style>''', unsafe_allow_html=True)
