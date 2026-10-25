
"""Aplicación grupal UNAP — portada narrativa y módulos originales."""

import streamlit as st

st.set_page_config(
    page_title="El Niño 2026–2027 | UNAP",
    page_icon="🌊",
    layout="wide",
)


def inicio():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2.5rem;
        }

        .eyebrow {
            font-size: .78rem;
            letter-spacing: .15em;
            color: #66757D;
            font-weight: 700;
        }

        .lead {
            font-size: 1.12rem;
            line-height: 1.75;
            color: #50636D;
            max-width: 780px;
        }

        .story {
            border-left: 3px solid #BD7141;
            padding: 12px 18px;
            background: #F7F8F8;
            margin: 12px 0 22px;
            line-height: 1.7;
            color: #172C39;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="eyebrow">'
        'UNAP · MAESTRÍA EN CIENCIA DE DATOS · VISUALIZACIÓN DE DATOS'
        '</div>',
        unsafe_allow_html=True,
    )

    st.title("El Niño 2026–2027: tres preguntas, tres modelos")

    st.markdown(
        '<div class="lead">'
        'Un recorrido por los antecedentes históricos del Pacífico, '
        'el aporte de ENSO a la estimación de lluvias en el Perú '
        'y una proyección experimental del indicador Niño 3.4.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("La historia en tres etapas")

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown("### 01 · ¿A qué se parece?")

        st.write(
            "**ML1 — Similitud histórica.** "
            "Compara patrones oceánicos de 2026 con episodios "
            "anteriores usando distancias estandarizadas."
        )

        st.caption(
            "Hallazgo: una analogía histórica no equivale "
            "a una predicción."
        )

        if st.button("Explorar ML1", use_container_width=True):
            st.switch_page("ml1/app.py")

    with c2:
        st.markdown("### 02 · ¿Ayuda a explicar la lluvia?")

        st.write(
            "**ML2 — Precipitaciones del Perú.** "
            "Compara modelos con y sin información ENSO "
            "en ubicaciones de referencia."
        )

        st.caption(
            "Hallazgo: ENSO mejoró 8 de 25 ubicaciones, "
            "sin una mejora global consistente."
        )

        if st.button("Explorar ML2", use_container_width=True):
            st.switch_page("ml2/app.py")

    with c3:
        st.markdown("### 03 · ¿Cómo podría evolucionar?")

        st.write(
            "**ML3 — Pronóstico Niño 3.4.** "
            "Visualiza una estimación experimental de seis meses "
            "y la compara con persistencia."
        )

        st.caption(
            "Hallazgo: Ridge no supera consistentemente "
            "a la referencia simple."
        )

        if st.button("Explorar ML3", use_container_width=True):
            st.switch_page("ml3/app.py")

    st.divider()

    st.subheader("Qué podemos concluir — y qué no")

    st.markdown(
        """
        <div class="story">
            <b>Lectura integrada.</b>
            Las similitudes históricas aportan contexto;
            la utilidad de ENSO para estimar lluvia cambia
            entre ubicaciones; y la proyección oceánica debe
            interpretarse con incertidumbre y validación.
            Son tres preguntas diferentes, no una cadena
            causal demostrada.
        </div>
        """,
        unsafe_allow_html=True,
    )

   


pages = [
    st.Page(
        inicio,
        title="Inicio · Historia de los datos",
        icon=":material/auto_stories:",
        url_path="inicio",
        default=True,
    ),
    st.Page(
        "ml1/app.py",
        title="ML 1 · Similitud histórica",
        icon=":material/history:",
        url_path="similitud-historica",
    ),
    st.Page(
        "ml2/app.py",
        title="ML 2 · Precipitaciones del Perú",
        icon=":material/rainy:",
        url_path="precipitaciones",
    ),
    st.Page(
        "ml3/app.py",
        title="ML 3 · Pronóstico Niño 3.4",
        icon=":material/show_chart:",
        url_path="pronostico",
    ),
]

pg = st.navigation(pages, position="sidebar")
pg.run()
