from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ML2 | El Niño y precipitaciones del Perú", layout="wide", initial_sidebar_state="expanded")
NAVY="#172C39"
COPPER="#BF7445"
TEAL="#087B83"
MUTED="#647987"
GRID="#E8EEF0"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html,body,.stApp,button,input,textarea,[data-testid="stSidebar"],[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],[data-testid="stMarkdownContainer"],[data-baseweb="tab"] {
 font-family:'DM Sans',Arial,sans-serif!important;
}
.stApp{color:#172C39}
.block-container{max-width:1150px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3{font-family:'DM Sans',Arial,sans-serif!important;color:#172C39!important;letter-spacing:-.025em}
h1{font-size:2.25rem!important;font-weight:700!important}
h3{font-size:1.25rem!important;font-weight:700!important}
[data-testid="stMetric"]{border:1px solid #DEE6EA;border-radius:4px;padding:14px 16px;background:#FAFBFB}
[data-testid="stMetricValue"]{font-weight:600!important}
[data-testid="stMetricLabel"]{color:#647987}
[data-testid="stSidebar"]{background:#F5F7F8}
.stTabs [data-baseweb="tab-list"]{gap:12px;border-bottom:1px solid #DEE6EA}
.stTabs [data-baseweb="tab"]{font-size:.88rem!important}
.stTabs [aria-selected="true"]{color:#BF7445!important}
.kicker{color:#BF7445;font-size:.75rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase}
.subtitle{color:#647987;font-size:.93rem;margin-top:-.5rem;margin-bottom:1.4rem}
.insight{background:#F7F8F8;border-left:3px solid #BF7445;padding:13px 17px;line-height:1.6;font-size:.91rem}
footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)

def layout(fig,height=430,right=110,ytitle="",legend=False):
    fig.update_layout(height=height,margin=dict(l=12,r=right,t=35,b=35),
        paper_bgcolor="white",plot_bgcolor="white",font=dict(family="DM Sans, Arial",size=12,color=NAVY),
        showlegend=legend,hovermode="closest")
    fig.update_xaxes(showgrid=False,linecolor="#CBD5DA",tickfont=dict(color=MUTED))
    fig.update_yaxes(title=ytitle,gridcolor=GRID,zerolinecolor="#BCCAD0",tickfont=dict(color=MUTED))
    return fig

ROOT=Path(__file__).resolve().parent
@st.cache_data
def load():
    folder=ROOT/"datos"
    p=pd.read_csv(folder/"01_predicciones_retrospectivas.csv",parse_dates=["fecha"])
    c=pd.read_csv(folder/"02_comparacion_nacional.csv")
    e=pd.read_csv(folder/"03_evaluacion_por_estado_ENSO.csv")
    d=pd.read_csv(folder/"02_dataset_nacional_noaa_power.csv")
    return p,c,e,d

P,C,E,D=load()
G=D[["departamento","latitud","longitud"]].drop_duplicates("departamento")
C=C.merge(G,on="departamento",how="left")
count=int((C["aporte_ENSO_pct"]>0).sum())

st.markdown('<p class="kicker">UNAP / Ciencia de datos / Visualización</p>',unsafe_allow_html=True)
st.title("El Niño y las precipitaciones del Perú")
st.markdown('<p class="subtitle">ML2 · Evaluación retrospectiva · NOAA CPC + NASA POWER · 25 ubicaciones de referencia</p>',unsafe_allow_html=True)
a,b,c=st.columns(3)
a.metric("Ubicaciones evaluadas",f"{len(C)}")
b.metric("Mejora al incluir ENSO",f"{count} de {len(C)}")
c.metric("Predicciones evaluadas",f"{len(P):,}")
st.write("")
t1,t2,t3,t4=st.tabs(["01 Panorama territorial","02 Evolución mensual","03 Comparación de modelos","04 Datos y método"])

with t1:
    st.markdown('<p class="kicker">Figura 01 / Comparación territorial</p>',unsafe_allow_html=True)
    st.subheader("¿Dónde aportó información El Niño?")
    st.caption("Valores positivos: ENSO redujo el error frente al modelo sin ENSO. Cada ubicación es un punto de referencia, no un promedio departamental.")
    view=C.sort_values("aporte_ENSO_pct",ascending=True)
    fig=go.Figure(go.Bar(
        x=view["aporte_ENSO_pct"],y=view["departamento"],orientation="h",
        marker_color=[TEAL if v>0 else "#A8B6BE" for v in view["aporte_ENSO_pct"]],
        customdata=np.stack([view["MAE_ENSO_mm"],view["MAE_meteo_mm"]],axis=-1),
        hovertemplate="<b>%{y}</b><br>Variación: %{x:+.1f}%<br>MAE con ENSO: %{customdata[0]:.1f} mm<br>MAE sin ENSO: %{customdata[1]:.1f} mm<extra></extra>"
    ))
    layout(fig,height=790,right=30)
    fig.update_layout(margin=dict(l=105,r=40,t=18,b=55),bargap=.27)
    fig.update_xaxes(title="Cambio relativo del error (%) · positivo = mejora",zeroline=True,zerolinecolor=NAVY)
    fig.update_yaxes(title="",showgrid=False,zeroline=False,tickfont=dict(size=12))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    st.markdown(f'<div class="insight"><b>Resultado:</b> incluir ENSO mejoró el modelo en {count} de {len(C)} ubicaciones; no se observó una mejora generalizada.</div>',unsafe_allow_html=True)

with t2:
    st.markdown('<p class="kicker">Figura 02 / Evolución mensual</p>',unsafe_allow_html=True)
    st.subheader("Precipitación observada y estimada")
    x,y=st.columns(2)
    places=sorted(P["departamento"].unique())
    years=sorted(P["anio"].unique())
    with x: place=st.selectbox("Ubicación de referencia",places,index=places.index("Puno") if "Puno" in places else 0)
    with y: year=st.selectbox("Año de evaluación",years,index=len(years)-1)
    s=P[(P["departamento"]==place)&(P["anio"]==year)].sort_values("mes")
    fig=go.Figure()
    for name,col,color,width,dash in [
        ("Observado","lluvia_mm_mes",NAVY,3.2,"solid"),
        ("Modelo sin ENSO","pred_meteo",TEAL,2.3,"solid"),
        ("Modelo ENSO","pred_enso",COPPER,2.5,"dash")
    ]:
        fig.add_trace(go.Scatter(x=s["mes"],y=s[col],name=name,mode="lines+markers",
            line=dict(color=color,width=width,dash=dash),marker=dict(size=5),
            hovertemplate=f"{name}: %{{y:.1f}} mm<extra></extra>"))
    layout(fig,height=465,right=35,ytitle="Precipitación mensual (mm)",legend=True)
    fig.update_layout(legend=dict(orientation="h",y=1.13,x=0,font=dict(size=12)),hovermode="x unified")
    fig.update_xaxes(tickvals=list(range(1,13)),ticktext=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"])
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    local=C[C["departamento"]==place].iloc[0]
    st.markdown(f'<div class="insight"><b>{place}:</b> MAE con ENSO {local["MAE_ENSO_mm"]:.1f} mm; sin ENSO {local["MAE_meteo_mm"]:.1f} mm. Evaluación retrospectiva, no pronóstico de 2026–2027.</div>',unsafe_allow_html=True)

with t3:
    st.markdown('<p class="kicker">Figura 03 / Evaluación de precisión</p>',unsafe_allow_html=True)
    st.subheader("¿Qué modelo tuvo menor error?")
    methods=[("Climatología","pred_climatologia"),("ML sin ENSO","pred_meteo"),("ML con ENSO","pred_enso")]
    vals=[float((P["lluvia_mm_mes"]-P[col]).abs().mean()) for _,col in methods]
    fig=go.Figure(go.Bar(x=[v[0] for v in methods],y=vals,
        marker_color=["#A3B0B6",TEAL,COPPER],
        text=[f"{v:.2f} mm" for v in vals],textposition="outside",
        hovertemplate="%{x}<br>MAE: %{y:.2f} mm<extra></extra>"))
    layout(fig,height=415,right=25,ytitle="Error absoluto medio (mm) · menor es mejor")
    fig.update_yaxes(range=[0,max(vals)*1.2])
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    st.markdown('<div class="insight"><b>Resultado:</b> el modelo con ENSO no redujo el error promedio global respecto a las referencias evaluadas.</div>',unsafe_allow_html=True)
    with st.expander("Consultar resultados por ubicación"):
        st.dataframe(C[["departamento","MAE_climatologia_mm","MAE_meteo_mm","MAE_ENSO_mm","aporte_ENSO_pct"]],use_container_width=True,hide_index=True)
        st.download_button("Descargar comparación (CSV)",C.to_csv(index=False).encode("utf-8-sig"),"evaluacion_ml2.csv","text/csv")

with t4:
    st.subheader("Datos y método")
    st.markdown("""**Fuentes.** NASA POWER: precipitación y temperatura mensual en 25 puntos de referencia del Perú. NOAA CPC: anomalías de las regiones Niño 1+2, Niño 3, Niño 3.4 y Niño 4.

**Datos.** 7 500 registros mensuales (25 ubicaciones × 300 meses).

**Modelo.** ExtraTrees con variables meteorológicas, comparado con una versión que incorpora ENSO y una referencia climatológica.

**Validación.** Predicciones retrospectivas de 2019, 2021, 2023 y 2025. Métrica: error absoluto medio (MAE).

**Alcance.** Los puntos de referencia no representan promedios departamentales. Los resultados no son alertas ni pronósticos operativos.""")
    with st.expander("Inspeccionar registros del dataset"):
        st.dataframe(D.head(30),use_container_width=True,hide_index=True)
st.divider()
st.caption("Universidad Nacional del Altiplano · Maestría en Ciencia de Datos · NOAA CPC y NASA POWER")
