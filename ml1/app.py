from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='ML 1 | Historia de El Niño', layout='wide', initial_sidebar_state='collapsed')

NAVY='#172C39'; COPPER='#BF7445'; MUTED='#6E818B'; GRID='#E8EEF0'
PALETTE=['#54758D','#82998C','#A28D73','#786D95','#667E86']
COLS={'Niño 3.4':'anom_nino34','Niño 1+2':'anom_nino12','Niño 3':'anom_nino3','Niño 4':'anom_nino4'}
MONTH={1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html,body,[class*="css"],.stApp,.stMarkdown,.stCaption,.stSelectbox,.stMultiSelect,
[data-testid="stMetric"],[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],h1,h2,h3,p,button {font-family:'DM Sans',sans-serif!important;}
.stApp{color:#172C39;background:white}
.block-container{max-width:1150px;padding-top:2.3rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.025em;color:#172C39!important;font-weight:700!important}
h1{font-size:2.25rem!important}h2{font-size:1.6rem!important}h3{font-size:1.2rem!important}
[data-testid="stMetric"]{padding:15px 16px;border:1px solid #E3E9EB;border-radius:4px;background:#FAFBFB}
[data-testid="stMetricLabel"]{color:#627783;font-size:.85rem}
[data-testid="stMetricValue"]{color:#172C39;font-weight:600}
.stTabs [data-baseweb="tab-list"]{gap:19px;border-bottom:1px solid #DFE6E9}
.stTabs [data-baseweb="tab"]{font-size:.87rem;font-weight:600}
.stTabs [aria-selected="true"]{color:#B76A3E!important;border-bottom-color:#B76A3E!important}
.kicker{color:#B76A3E;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem;font-weight:700;margin:0 0 6px}
.subtitle{color:#667984;font-size:.95rem;margin-top:-.3rem;margin-bottom:1.6rem}
.insight{border-left:3px solid #B76A3E;background:#F7F9FA;padding:14px 18px;color:#2E4856;font-size:.91rem;line-height:1.55}
[data-testid="stSidebar"]{background:#F5F7F8}
footer{visibility:hidden}
</style>''', unsafe_allow_html=True)

def chart_layout(fig,height=420,right=130,ytitle=''):
    fig.update_layout(height=height,margin=dict(l=8,r=right,t=28,b=28),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans, Arial, sans-serif',size=12,color=NAVY),
        showlegend=False,hovermode='x unified')
    fig.update_xaxes(showgrid=False,linecolor='#C6D1D6',ticks='',tickfont=dict(color=MUTED))
    fig.update_yaxes(title=ytitle,gridcolor=GRID,zeroline=True,
                     zerolinecolor='#B9C6CB',tickfont=dict(color=MUTED))
    return fig

def label_ends(fig,lines,min_gap=.16):
    ordered=sorted(lines,key=lambda a:a[2]); adjusted=[]
    for name,x,y,color in ordered:
        pos=max(y,adjusted[-1][1]+min_gap) if adjusted else y
        adjusted.append((name,pos,x,y,color))
    for name,pos,x,y,color in adjusted:
        fig.add_annotation(x=x,y=y,ax=42,ay=-((pos-y)*75),xref='x',yref='y',
            axref='pixel',ayref='pixel',text=name,showarrow=True,arrowhead=0,
            arrowwidth=.8,arrowcolor=color,xanchor='left',
            font=dict(size=11,color=color),bgcolor='rgba(255,255,255,.9)',borderpad=2)

ROOT=Path(__file__).resolve().parent
@st.cache_data
def load():
    folder=ROOT/'datos'
    names=['enso_dataset_maestro.csv','01_ranking_similitud.csv','02_validacion_retrospectiva.csv']
    missing=[n for n in names if not (folder/n).is_file()]
    if missing:
        st.error('Faltan datos originales del ML1 en ml1/datos/: '+', '.join(missing))
        st.stop()
    return tuple(pd.read_csv(folder/n,encoding='utf-8-sig') for n in names)
D,R,V=load()
R=R.sort_values('distancia_ml_estandarizada',ascending=True).reset_index(drop=True)

st.markdown('<p class="kicker">UNAP / Ciencia de datos / Visualización</p>',unsafe_allow_html=True)
st.title('¿A qué episodios históricos se parece 2026?')
st.markdown('<p class="subtitle">ML 1 · Similitud histórica mediante distancias estandarizadas · NOAA CPC · Datos hasta septiembre de 2026</p>',unsafe_allow_html=True)
latest=float(D.query('anio == 2026 and mes == 9')['anom_nino34'].iloc[0])
a,b,c=st.columns(3)
a.metric('Niño 3.4 · septiembre 2026',f'{latest:+.2f} °C')
b.metric('Episodio más cercano',str(int(R.iloc[0]['anio_historico'])))
c.metric('Años históricos comparados',str(len(R)))
st.markdown('')
t1,t2,t3,t4=st.tabs(['01  Comparación temporal','02  Ranking histórico','03  Regiones del Pacífico','04  Método y validación'])

with t1:
    st.markdown('<p class="kicker">Figura 01 / Evolución comparada</p>',unsafe_allow_html=True)
    st.subheader('El patrón de 2026 frente a otros años')
    c1,c2,c3=st.columns([1.1,2,1.2])
    with c1: region=st.selectbox('Región oceánica',list(COLS),key='ml1_region')
    with c2:
        options=R.anio_historico.astype(int).tolist()
        years=st.multiselect('Años históricos',options,default=options[:3],max_selections=5,key='ml1_years')
    with c3: extend=st.toggle('Ver meses posteriores históricos',value=False,key='ml1_extend')
    months=list(range(5,13)) if extend else list(range(5,10))
    fig=go.Figure(); ends=[]
    for i,year in enumerate(years):
        s=D[(D.anio==year)&(D.mes.isin(months))].sort_values('mes')
        if s.empty: continue
        color=PALETTE[i%len(PALETTE)]
        fig.add_trace(go.Scatter(x=s.mes,y=s[COLS[region]],mode='lines+markers',
            name=str(year),line=dict(color=color,width=2),marker=dict(size=5),
            hovertemplate=f'{year}: '+'%{y:+.2f} °C<extra></extra>'))
        ends.append((str(year),int(s.mes.iloc[-1]),float(s[COLS[region]].iloc[-1]),color))
    current=D[(D.anio==2026)&(D.mes.between(5,9))].sort_values('mes')
    fig.add_trace(go.Scatter(x=current.mes,y=current[COLS[region]],mode='lines+markers',
        name='2026 observado',line=dict(color=COPPER,width=3.4),marker=dict(size=7),
        hovertemplate='2026: %{y:+.2f} °C<extra></extra>'))
    ends.append(('2026 · NOAA',9,float(current[COLS[region]].iloc[-1]),COPPER))
    fig.update_xaxes(tickvals=months,ticktext=[MONTH[m] for m in months],range=[4.8,max(months)+1.3])
    chart_layout(fig,465,160,'Anomalía oceánica (°C)');label_ends(fig,ends)
    st.plotly_chart(fig,use_container_width=True,key='ml1_chart_01')
    st.markdown('<div class="insight">Las líneas históricas son mediciones de años anteriores. Si se muestran meses posteriores a septiembre, <b>no son un pronóstico de 2026</b>. La similitud se calculó con cuatro regiones y los meses de mayo a septiembre.</div>',unsafe_allow_html=True)

with t2:
    st.markdown('<p class="kicker">Figura 02 / Distancia entre patrones</p>',unsafe_allow_html=True)
    st.subheader('Los diez años más parecidos')
    top=R.nsmallest(10,'distancia_ml_estandarizada').copy()
    top['anio_etiqueta']=top['anio_historico'].astype(int).astype(str)
    # Eje categórico explícito: evita que Plotly convierta los años en una escala continua.
    # El año más cercano queda arriba; cada barra tiene su propia categoría.
    fig=go.Figure(go.Bar(
        x=top['distancia_ml_estandarizada'],y=top['anio_etiqueta'],orientation='h',
        marker=dict(color=[COPPER if i==0 else '#91A5AE' for i in range(len(top))]),
        text=[f'{v:.2f}' for v in top['distancia_ml_estandarizada']],
        textposition='outside',textfont=dict(size=13,color=NAVY),cliponaxis=False,
        customdata=top['anio_etiqueta'],
        hovertemplate='Año %{customdata} · Distancia %{x:.2f}<extra></extra>'))
    chart_layout(fig,490,85)
    fig.update_layout(hovermode='closest',bargap=.38)
    fig.update_yaxes(type='category',categoryorder='array',
        categoryarray=top['anio_etiqueta'].tolist(),autorange='reversed',
        title='',showgrid=False,zeroline=False,tickfont=dict(size=13,color=NAVY))
    fig.update_xaxes(title='Distancia estandarizada · menor indica mayor similitud',
        range=[0,float(top['distancia_ml_estandarizada'].max())*1.17],
        showgrid=True,gridcolor=GRID,zeroline=False)
    st.plotly_chart(fig,use_container_width=True,key='ml1_chart_02')
    st.caption('La distancia mide semejanza entre patrones históricos; no representa una probabilidad de que 2026 evolucione igual.')
    with st.expander('Consultar ranking completo y descargar CSV'):
        st.dataframe(R,use_container_width=True,hide_index=True)
        st.download_button('Descargar ranking',R.to_csv(index=False).encode('utf-8-sig'),
            'ranking_ml1.csv','text/csv',key='ml1_download_ranking')

with t3:
    st.markdown('<p class="kicker">Figura 03 / Regiones oceánicas</p>',unsafe_allow_html=True)
    st.subheader('Ubicación esquemática de las regiones Niño')
    st.caption('Las anomalías corresponden a la temperatura superficial del mar, no a la temperatura del aire en Perú.')
    fig=go.Figure()
    regions=[('Niño 4',160,210,-5,5,'#6C8B95'),('Niño 3.4',190,240,-5,5,COPPER),
             ('Niño 3',210,270,-5,5,'#54758D'),('Niño 1+2',270,280,-10,0,'#A18D74')]
    for name,x0,x1,y0,y1,color in regions:
        fig.add_shape(type='rect',x0=x0,x1=x1,y0=y0,y1=y1,
            line=dict(color=color,width=2),fillcolor=color,opacity=.19)
        fig.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2,text=name,showarrow=False,
            font=dict(color=NAVY,size=12),bgcolor='rgba(255,255,255,.85)')
    fig.update_layout(height=280,margin=dict(l=20,r=20,t=15,b=15),
        font=dict(family='DM Sans, Arial, sans-serif',color=NAVY),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#F5F8F9',
        xaxis=dict(title='Longitud en grados Este (0–360)',range=[145,285],
            tickvals=[160,180,200,220,240,260,280],gridcolor=GRID),
        yaxis=dict(title='Latitud',range=[-16,12],gridcolor=GRID),showlegend=False)
    st.plotly_chart(fig,use_container_width=True,key='ml1_chart_03')
    st.caption('Esquema de límites geográficos, no mapa costero a escala. Las regiones se superponen porque sus áreas de medición también lo hacen.')
    values=D.query('anio == 2026 and mes == 9').iloc[0]
    boxes=st.columns(4)
    for box,(name,col) in zip(boxes,COLS.items()): box.metric(name,f'{values[col]:+.2f} °C')

with t4:
    st.subheader('Cómo se construyó ML 1')
    st.markdown('''**Datos.** Archivo NOAA CPC mensual desde enero de 1982 hasta septiembre de 2026. Se utilizaron las anomalías de Niño 1+2, Niño 3, Niño 3.4 y Niño 4.

**Preparación.** Para cada año se extrajeron mayo–septiembre (cinco meses × cuatro regiones = 20 variables). Las variables se estandarizaron para comparar distancias.

**Método.** Búsqueda de vecinos históricos más cercanos mediante distancia euclidiana en el espacio estandarizado; el resultado es un ranking de semejanza, no una clasificación probabilística.

**Validación.** Comparación retrospectiva de años anteriores con sus análogos disponibles. El RMSE reconstruye patrones históricos y **no es una medida de precisión de un pronóstico futuro**.

**Limitación.** Una coincidencia de anomalías oceánicas no garantiza el mismo comportamiento futuro ni determina lluvias locales en Perú.''')
    m1,m2=st.columns(2)
    m1.metric('Comparaciones retrospectivas',len(V))
    m2.metric('RMSE medio de reconstrucción',f'{V.rmse_4_indices_c.mean():.2f} °C')
    with st.expander('Revisar validación retrospectiva'):
        st.dataframe(V,use_container_width=True,hide_index=True)
st.divider()
st.caption('Universidad Nacional del Altiplano · Maestría en Ciencia de Datos · Fuente: NOAA CPC · Análisis académico experimental')
