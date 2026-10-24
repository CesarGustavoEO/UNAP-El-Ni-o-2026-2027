"""ML2 V3 | ENSO y precipitación en 25 puntos del Perú.
Ejecutar: python 09_ml2_peru_v3.py
Requiere: pandas numpy scikit-learn matplotlib
Datos: 02_dataset_nacional_noaa_power.csv del ML2 anterior.
IMPORTANTE: los puntos NO representan promedios departamentales.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent
CANDIDATES = [ROOT/'02_dataset_nacional_noaa_power.csv', ROOT/'datos_procesados'/'02_dataset_nacional_noaa_power.csv', ROOT/'ML2_Peru_V2'/'02_dataset_nacional_noaa_power.csv']
SOURCE = next((p for p in CANDIDATES if p.is_file()), None)
if SOURCE is None:
    sys.exit('ERROR: coloca 02_dataset_nacional_noaa_power.csv junto a este programa o en datos_procesados.')
OUT = ROOT/'resultados_ml2_v3'
OUT.mkdir(exist_ok=True)
START_TEST, END_TEST = 2019, 2025
ENSO = ['anom_nino34','anom_nino12','anom_nino3','anom_nino4']

raw = pd.read_csv(SOURCE, encoding='utf-8-sig')
required = ['departamento','anio','mes','lluvia_mm_mes','temperatura_c'] + ENSO
missing = sorted(set(required)-set(raw.columns))
if missing: sys.exit(f'ERROR: faltan columnas {missing}')
raw['fecha'] = pd.to_datetime(dict(year=raw.anio,month=raw.mes,day=1))
raw = raw.sort_values(['departamento','fecha']).reset_index(drop=True)
if raw.duplicated(['departamento','fecha']).any(): sys.exit('ERROR: hay meses duplicados por ubicación.')
raw['lluvia_mm_mes'] = pd.to_numeric(raw.lluvia_mm_mes,errors='coerce')
raw.loc[raw.lluvia_mm_mes < 0, 'lluvia_mm_mes'] = np.nan
# Para un pronóstico con un mes de antelación, solo se permiten variables observadas
# hasta el mes anterior. No se usan anomalías precomputadas con climatología futura.
grp = raw.groupby('departamento',sort=False)
for lag in [1,2,3,6,12]:
    raw[f'lluvia_lag{lag}'] = grp['lluvia_mm_mes'].shift(lag)
for lag in [1,2,3]:
    raw[f'temp_lag{lag}'] = grp['temperatura_c'].shift(lag)
for idx in ENSO:
    for lag in [1,2,3,6]:
        raw[f'{idx}_lag{lag}'] = grp[idx].shift(lag)
raw['mes_sin'] = np.sin(2*np.pi*raw.mes/12)
raw['mes_cos'] = np.cos(2*np.pi*raw.mes/12)
weather_cols = [f'lluvia_lag{x}' for x in [1,2,3,6,12]] + [f'temp_lag{x}' for x in [1,2,3]] + ['mes_sin','mes_cos']
enso_cols = [f'{x}_lag{lag}' for x in ENSO for lag in [1,2,3,6]]

# Clases de episodio SOLO para estratificación descriptiva, basadas en Niño3.4
# observado el mes previo. Umbral +/-0.5 °C, no es clasificación oficial ONI.
raw['estado_enso_previo'] = np.select([raw['anom_nino34_lag1']>=0.5,raw['anom_nino34_lag1']<=-0.5],['Calido','Frio'],default='Neutral')

predictions=[]
print(f'Fuente: {SOURCE.name} | {len(raw)} filas | {raw.departamento.nunique()} ubicaciones')
print('Validación: años 2019, 2021, 2023 y 2025; cada año entrena solo con años anteriores.')
for loc, frame in raw.groupby('departamento',sort=True):
    frame=frame.copy()
    for test_year in [2019,2021,2023,2025]:
        train=frame[(frame.anio<test_year)&(frame.anio>=2002)].copy()
        test=frame[frame.anio==test_year].copy()
        train=train.dropna(subset=['lluvia_mm_mes']+weather_cols+enso_cols)
        test=test.dropna(subset=['lluvia_mm_mes']+weather_cols+enso_cols)
        if len(train)<90 or test.empty: continue
        # Climatología entrenada exclusivamente con el pasado (sin fuga temporal).
        monthly=train.groupby('mes')['lluvia_mm_mes'].mean()
        test['pred_climatologia']=test.mes.map(monthly)
        # Dos algoritmos idénticos, excepto por la información ENSO.
        models=[]
        for cols in [weather_cols,weather_cols+enso_cols]:
            m=ExtraTreesRegressor(n_estimators=24,min_samples_leaf=5,max_features=0.85,random_state=42,n_jobs=-1)
            m.fit(train[cols],train['lluvia_mm_mes'])
            models.append(m.predict(test[cols]).clip(min=0))
        test['pred_meteo']=models[0]
        test['pred_enso']=models[1]
        predictions.append(test[['departamento','fecha','anio','mes','lluvia_mm_mes','estado_enso_previo','pred_climatologia','pred_meteo','pred_enso']])
    print(f'  {loc}: terminado')
if not predictions: sys.exit('ERROR: no hay suficientes datos históricos para validar.')
pred=pd.concat(predictions,ignore_index=True)
pred['evento_extremo'] = False
# Umbral del percentil 90 estimado solamente con observaciones PREVIAS a cada año
for (loc,yr), ids in pred.groupby(['departamento','anio']).groups.items():
    history=raw[(raw.departamento==loc)&(raw.anio<yr)&(raw.anio>=2002)].lluvia_mm_mes.dropna()
    if len(history)>60:
        pred.loc[ids,'evento_extremo']=pred.loc[ids,'lluvia_mm_mes']>=history.quantile(0.90)
for model in ['climatologia','meteo','enso']:
    pred[f'error_{model}']=abs(pred.lluvia_mm_mes-pred[f'pred_{model}'])
pred.to_csv(OUT/'01_predicciones_retrospectivas.csv',index=False,encoding='utf-8-sig')

rows=[]
for loc,g in pred.groupby('departamento'):
    a,b,c=(g[f'error_{x}'].mean() for x in ['climatologia','meteo','enso'])
    rows.append({'departamento':loc,'meses':len(g),'MAE_climatologia_mm':a,'MAE_meteo_mm':b,'MAE_ENSO_mm':c,
                 'aporte_ENSO_pct':100*(b-c)/b if b else np.nan,
                 'mejora_vs_climatologia_pct':100*(a-c)/a if a else np.nan,
                 'n_extremos':int(g.evento_extremo.sum()),
                 'MAE_extremos_meteo_mm':g.loc[g.evento_extremo,'error_meteo'].mean(),
                 'MAE_extremos_ENSO_mm':g.loc[g.evento_extremo,'error_enso'].mean()})
summary=pd.DataFrame(rows).sort_values('aporte_ENSO_pct',ascending=False)
summary.to_csv(OUT/'02_comparacion_nacional.csv',index=False,encoding='utf-8-sig',float_format='%.3f')

strata=[]
for (loc,state),g in pred.groupby(['departamento','estado_enso_previo']):
    if len(g)<5: continue
    strata.append({'departamento':loc,'estado_previo':state,'n_meses':len(g),
                   'MAE_meteo_mm':g.error_meteo.mean(),'MAE_ENSO_mm':g.error_enso.mean(),
                   'aporte_ENSO_pct':100*(g.error_meteo.mean()-g.error_enso.mean())/g.error_meteo.mean() if g.error_meteo.mean() else np.nan})
pd.DataFrame(strata).to_csv(OUT/'03_evaluacion_por_estado_ENSO.csv',index=False,encoding='utf-8-sig',float_format='%.3f')

fig,ax=plt.subplots(figsize=(11,10))
plot=summary.sort_values('aporte_ENSO_pct')
colors=['#16826d' if v>0 else '#b65745' for v in plot.aporte_ENSO_pct]
ax.barh(plot.departamento,plot.aporte_ENSO_pct,color=colors,height=.74)
ax.axvline(0,color='#333333',lw=1)
ax.set_xlabel('Reducción del error al añadir índices ENSO (%)  |  positivo = mejora')
ax.set_title('¿Dónde ayudan los índices de El Niño a estimar lluvias?\n25 puntos de referencia del Perú · evaluación retrospectiva 2019, 2021, 2023 y 2025',pad=15)
ax.grid(axis='x',alpha=.15)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT/'04_aporte_ENSO_por_ubicacion.png',dpi=170,bbox_inches='tight')
plt.close(fig)

fig,ax=plt.subplots(figsize=(10,5))
byyear=pred.groupby('anio')[['error_climatologia','error_meteo','error_enso']].mean()
for col,label,color in [('error_climatologia','Climatología','#777777'),('error_meteo','ML sin ENSO','#2465a5'),('error_enso','ML con ENSO','#b65745')]:
    ax.plot(byyear.index,byyear[col],marker='o',lw=2,label=label,color=color)
ax.set_title('¿Qué modelo se equivoca menos en cada año?')
ax.set_xlabel('Año de evaluación');ax.set_ylabel('Error absoluto medio (mm/mes)')
ax.legend(frameon=False,ncol=3,loc='upper center');ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(OUT/'05_validacion_por_anio.png',dpi=170,bbox_inches='tight');plt.close(fig)

n=(summary.aporte_ENSO_pct>0).sum()
print(f'\nFINALIZADO: ENSO mejora en {n} de {len(summary)} puntos de referencia.')
print(f'Archivos guardados en: {OUT}')
print('IMPORTANTE: no son promedios departamentales ni predicciones de riesgo.')
print('Los episodios cálidos/fríos usan umbrales exploratorios de Niño3.4 mensual, no ONI oficial.')
