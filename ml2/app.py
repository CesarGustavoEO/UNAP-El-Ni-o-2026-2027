from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
st.set_page_config(page_title='ML 2 | El Niño y lluvias del Perú',layout='wide',initial_sidebar_state='collapsed')

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600;700&display=swap');
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;color:#172C39}
.block-container{max-width:1150px;padding-top:2.3rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Source Serif 4',Georgia,serif!important;letter-spacing:-.02em;color:#172C39}
h1{font-size:2.55rem!important}h2{font-size:1.65rem!important}h3{font-size:1.24rem!important}
[data-testid="stMetric"]{padding:15px 16px;border:1px solid #E3E9EB;border-radius:4px;background:#FAFBFB}
[data-testid="stMetricLabel"]{color:#627783;font-size:.85rem}
[data-testid="stMetricValue"]{font-family:Georgia,serif;color:#172C39}
.stTabs [data-baseweb="tab-list"]{gap:19px;border-bottom:1px solid #DFE6E9}
.stTabs [data-baseweb="tab"]{font-size:.87rem;font-weight:600}
.stTabs [aria-selected="true"]{color:#B76A3E!important;border-bottom-color:#B76A3E!important}
.kicker{color:#B76A3E;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem;font-weight:700;margin:0 0 6px}
.subtitle{color:#667984;font-size:.95rem;margin-top:-.3rem;margin-bottom:1.6rem}
.caption-note{font-size:.81rem;color:#758690;line-height:1.6}
.insight{border-left:3px solid #B76A3E;background:#F7F9FA;padding:14px 18px;color:#2E4856;font-size:.91rem;line-height:1.55}
[data-testid="stSidebar"]{background:#F5F7F8}
footer{visibility:hidden}
</style>""",unsafe_allow_html=True)

NAVY='#172C39';TEAL='#087B83';COPPER='#BF7445';MUTED='#6E818B';GRID='#E8EEF0'
def chart_layout(fig, height=420, right=150, ytitle=''):
    fig.update_layout(height=height,margin=dict(l=8,r=right,t=28,b=20),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Arial',size=12,color=NAVY),showlegend=False,hovermode='x unified')
    fig.update_xaxes(showgrid=False,linecolor='#C6D1D6',ticks='',tickfont=dict(color=MUTED))
    fig.update_yaxes(title=ytitle,gridcolor=GRID,zeroline=True,zerolinecolor='#B9C6CB',tickfont=dict(color=MUTED))
    return fig

def label_ends(fig, lines, fmt='{:.2f}', min_gap=.16):
    # lines: (name, x_end, y_end, color); place labels at end and deconflict close values
    ordered=sorted(lines,key=lambda a:a[2]); adjusted=[]
    for name,x,y,color in ordered:
        pos=max(y, adjusted[-1][1]+min_gap) if adjusted else y
        adjusted.append((name,pos,x,y,color))
    for name,pos,x,y,color in adjusted:
        fig.add_annotation(x=x,y=y,ax=40,ay=-((pos-y)*75),xref='x',yref='y',axref='pixel',ayref='pixel',text=name,showarrow=True,arrowhead=0,arrowsize=1,arrowwidth=.8,arrowcolor=color,xanchor='left',font=dict(size=11,color=color),bgcolor='rgba(255,255,255,.88)',borderpad=2)

ROOT=Path(__file__).resolve().parent
@st.cache_data
def load():
    p=pd.read_csv(ROOT/'datos'/'01_predicciones_retrospectivas.csv',parse_dates=['fecha'])
    c=pd.read_csv(ROOT/'datos'/'02_comparacion_nacional.csv')
    e=pd.read_csv(ROOT/'datos'/'03_evaluacion_por_estado_ENSO.csv')
    d=pd.read_csv(ROOT/'datos'/'02_dataset_nacional_noaa_power.csv')
    return p,c,e,d
P,C,E,D=load()
G=D[['departamento','latitud','longitud']].drop_duplicates('departamento')
C=C.merge(G,on='departamento',how='left')
count=int((C.aporte_ENSO_pct>0).sum())
st.markdown('<p class="kicker">UNAP / Ciencia de datos / Visualización</p>',unsafe_allow_html=True)
st.title('El Niño y las precipitaciones del Perú')
st.markdown('<p class="subtitle">ML 2 · Evaluación retrospectiva de modelos · NOAA CPC + NASA POWER · 25 ubicaciones de referencia</p>',unsafe_allow_html=True)
a,b,c=st.columns(3)
a.metric('Ubicaciones evaluadas',str(len(C)))
b.metric('Mejora al incluir ENSO',f'{count} de {len(C)}')
c.metric('Predicciones evaluadas',f'{len(P):,}')
st.markdown('')
t1,t2,t3,t4=st.tabs(['01  Panorama territorial','02  Evolución mensual','03  Comparación de modelos','04  Datos y método'])
with t1:
    st.markdown('<p class="kicker">Figura 01 / Comparación territorial</p>',unsafe_allow_html=True)
    st.subheader('¿Dónde aportó información El Niño?')
    st.caption('Un valor positivo indica que añadir indicadores ENSO redujo el error frente al modelo meteorológico sin ENSO. Cada lugar es un punto de referencia, no un promedio departamental.')
    view=C.sort_values('aporte_ENSO_pct')
    colors=[TEAL if x>0 else '#B9C5CA' for x in view.aporte_ENSO_pct]
    fig=go.Figure(go.Bar(x=view.aporte_ENSO_pct,y=view.departamento,orientation='h',marker_color=colors,customdata=np.stack([view.MAE_ENSO_mm,view.MAE_meteo_mm],axis=-1),hovertemplate='%{y}<br>Mejora ENSO: %{x:+.1f}%<br>MAE ENSO: %{customdata[0]:.1f} mm<br>MAE sin ENSO: %{customdata[1]:.1f} mm<extra></extra>'))
    chart_layout(fig,690,25,'Cambio relativo del error (%) · positivo = mejora')
    fig.update_yaxes(title='',showgrid=False,zeroline=False,tickfont=dict(size=11))
    fig.update_xaxes(zeroline=True,zerolinecolor='#6D808A')
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="insight">La incorporación de ENSO mejoró el modelo en <b>'+str(count)+' de 25 ubicaciones</b>, pero no en todas. Por eso no se puede afirmar que las variables ENSO mejoren la predicción de lluvias en todo el Perú.</div>',unsafe_allow_html=True)
with t2:
    st.markdown('<p class="kicker">Figura 02 / Series temporales</p>',unsafe_allow_html=True)
    st.subheader('Lluvia observada y estimada en una ubicación')
    x,y=st.columns([1,1])
    with x: place=st.selectbox('Ubicación de referencia',sorted(P.departamento.unique()),index=sorted(P.departamento.unique()).index('Puno'))
    with y: year=st.selectbox('Año de evaluación',sorted(P.anio.unique()),index=len(P.anio.unique())-1)
    s=P[(P.departamento==place)&(P.anio==year)].sort_values('mes')
    fig=go.Figure(); lines=[]
    series=[('Observado', 'lluvia_mm_mes',NAVY,3.1,'solid'),('Modelo ENSO','pred_enso',COPPER,2.5,'dash'),('Modelo sin ENSO','pred_meteo',TEAL,2,'solid')]
    for name,col,color,width,dash in series:
        fig.add_trace(go.Scatter(x=s.mes,y=s[col],mode='lines+markers',line=dict(color=color,width=width,dash=dash),marker=dict(size=5),name=name,hovertemplate=name+': %{y:.1f} mm<extra></extra>'))
        lines.append((name,int(s.mes.iloc[-1]),float(s[col].iloc[-1]),color))
    chart_layout(fig,460,185,'Precipitación mensual (mm)')
    fig.update_xaxes(tickvals=list(range(1,13)),ticktext=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],range=[.8,14.5])
    label_ends(fig,lines,min_gap=max(4,float(s.lluvia_mm_mes.max())*.045))
    st.plotly_chart(fig,use_container_width=True)
    local=C[C.departamento==place].iloc[0]
    st.markdown(f'<div class="insight"><b>{place}.</b> El error medio fue {local.MAE_ENSO_mm:.1f} mm con ENSO y {local.MAE_meteo_mm:.1f} mm sin ENSO. Se trata de predicciones retrospectivas, no de un pronóstico para 2026–2027.</div>',unsafe_allow_html=True)
with t3:
    st.markdown('<p class="kicker">Figura 03 / Evaluación de precisión</p>',unsafe_allow_html=True)
    st.subheader('¿Qué modelo se equivocó menos?')
    methods=[('Climatología','pred_climatologia'),('ML sin ENSO','pred_meteo'),('ML con ENSO','pred_enso')]
    vals=[float((P.lluvia_mm_mes-P[col]).abs().mean()) for _,col in methods]
    fig=go.Figure(go.Bar(x=[m[0] for m in methods],y=vals,marker_color=['#A3B0B6',TEAL,COPPER],text=[f'{v:.2f} mm' for v in vals],textposition='outside',hovertemplate='%{x}: %{y:.2f} mm<extra></extra>'))
    chart_layout(fig,390,35,'Error absoluto medio (mm) · menor es mejor')
    fig.update_yaxes(range=[0,max(vals)*1.18])
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="insight">En esta evaluación, añadir ENSO <b>no redujo el error medio global</b> frente a las otras referencias. Un resultado negativo también es un hallazgo válido cuando se muestra con transparencia.</div>',unsafe_allow_html=True)
    with st.expander('Consultar resultados por ubicación'):
        st.dataframe(C[['departamento','MAE_climatologia_mm','MAE_meteo_mm','MAE_ENSO_mm','aporte_ENSO_pct']],use_container_width=True,hide_index=True)
        st.download_button('Descargar comparación',C.to_csv(index=False).encode('utf-8-sig'),'evaluacion_ml2.csv','text/csv')
with t4:
    st.subheader('Cómo se construyó ML 2')
    st.markdown("""**Fuentes.** NASA POWER: precipitación y temperatura mensuales en 25 coordenadas de referencia del Perú. NOAA CPC: anomalías oceánicas de las regiones Niño 1+2, Niño 3, Niño 3.4 y Niño 4.

**Dataset.** 7 500 registros mensuales (25 ubicaciones × 300 meses). Las series se integraron por año y mes.

**Método.** Se comparó un modelo ExtraTrees con variables meteorológicas frente a otro que también incluye indicadores ENSO, además de una referencia climatológica.

**Validación.** Predicciones retrospectivas de 2019, 2021, 2023 y 2025 (48 meses por ubicación). Se evaluó el error absoluto medio (MAE): cuanto menor, mejor.

**Alcance.** Los 25 puntos no equivalen a promedios de departamentos ni permiten generalizar resultados a todas las comunidades o parcelas. No se ofrecen alertas de inundación ni pronósticos operativos.""")
    st.caption('Los datos y resultados del análisis se incluyen para su inspección y reproducción. El script 09_ml2_peru_v3.py documenta el entrenamiento.')
    with st.expander('Inspeccionar las primeras filas del dataset'):
        st.dataframe(D.head(30),use_container_width=True,hide_index=True)
st.divider()
st.caption('Universidad Nacional del Altiplano · Maestría en Ciencia de Datos · Fuentes: NOAA CPC y NASA POWER · Investigación académica')
