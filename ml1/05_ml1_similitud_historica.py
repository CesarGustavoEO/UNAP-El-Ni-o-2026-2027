"""ML 1: vecinos más cercanos de episodios ENSO, mayo-septiembre.

Uso: python 05_ml1_similitud_historica.py
Requiere: pandas numpy matplotlib scikit-learn
Lee: datos_procesados/enso_dataset_maestro.csv
Genera: resultados_ml1/*.csv y *.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / 'datos_procesados' / 'enso_dataset_maestro.csv'
SALIDA = BASE / 'resultados_ml1'
SALIDA.mkdir(exist_ok=True)
VARIABLES = ['anom_nino12', 'anom_nino3', 'anom_nino34', 'anom_nino4']
MESES = [5, 6, 7, 8, 9]
ANIO_OBJETIVO = 2026

if not ARCHIVO.exists():
    raise FileNotFoundError(f'No encuentro {ARCHIVO}. Coloca este script en la carpeta principal del proyecto.')

datos = pd.read_csv(ARCHIVO)
for campo in ['anio', 'mes'] + VARIABLES:
    if campo not in datos.columns:
        raise ValueError(f'Falta la columna {campo}')
    datos[campo] = pd.to_numeric(datos[campo], errors='coerce')

if datos.duplicated(['anio', 'mes']).any():
    raise ValueError('Hay fechas duplicadas: revisar dataset maestro.')

# Una observación = la trayectoria mayo-septiembre de un año, en cuatro regiones.
ventanas = {}
for anio, grupo in datos[datos['mes'].isin(MESES)].groupby('anio'):
    grupo = grupo.set_index('mes').reindex(MESES)
    if grupo[VARIABLES].notna().all().all():
        ventanas[int(anio)] = grupo[VARIABLES].to_numpy(dtype=float)

if ANIO_OBJETIVO not in ventanas:
    raise ValueError('No están completos mayo-septiembre de 2026.')

anios_historicos = sorted(y for y in ventanas if y < ANIO_OBJETIVO)
if len(anios_historicos) < 10:
    raise ValueError('Insuficientes años históricos completos.')

X = np.stack([ventanas[y].ravel() for y in anios_historicos])
y_actual = ventanas[ANIO_OBJETIVO].ravel().reshape(1, -1)

# Estandarización aprendida EXCLUSIVAMENTE de años anteriores a 2026.
escalador = StandardScaler().fit(X)
X_std = escalador.transform(X)
actual_std = escalador.transform(y_actual)

modelo = NearestNeighbors(n_neighbors=len(anios_historicos), metric='euclidean')
modelo.fit(X_std)
distancias, indices = modelo.kneighbors(actual_std)

ranking = []
for orden, (dist, idx) in enumerate(zip(distancias[0], indices[0]), start=1):
    anio = anios_historicos[idx]
    rmse = float(np.sqrt(np.mean((ventanas[anio] - ventanas[ANIO_OBJETIVO]) ** 2)))
    ranking.append({'puesto': orden, 'anio_historico': anio,
                    'distancia_ml_estandarizada': float(dist), 'rmse_4_indices_c': rmse})
resultado = pd.DataFrame(ranking)
resultado.to_csv(SALIDA / '01_ranking_similitud.csv', index=False, encoding='utf-8-sig')

# Validación retrospectiva: cada año histórico se compara con años anteriores.
# Es una prueba de recuperación de análogos, NO de precisión de pronóstico futuro.
pruebas = []
for objetivo in anios_historicos:
    candidatos = [y for y in anios_historicos if y < objetivo]
    if len(candidatos) < 10:
        continue
    train = np.stack([ventanas[y].ravel() for y in candidatos])
    scaler = StandardScaler().fit(train)
    vecinos = NearestNeighbors(n_neighbors=1).fit(scaler.transform(train))
    d, ix = vecinos.kneighbors(scaler.transform(ventanas[objetivo].ravel().reshape(1, -1)))
    analogo = candidatos[int(ix[0, 0])]
    pruebas.append({'anio_evaluado': objetivo, 'analogo_previo': analogo,
                    'rmse_4_indices_c': float(np.sqrt(np.mean((ventanas[objetivo] - ventanas[analogo]) ** 2)))})
validacion = pd.DataFrame(pruebas)
validacion.to_csv(SALIDA / '02_validacion_retrospectiva.csv', index=False, encoding='utf-8-sig')

# Dataset listo para Streamlit: una fila por mes y año comparado.
seleccionados = [ANIO_OBJETIVO] + resultado.head(3)['anio_historico'].astype(int).tolist()
filas = []
for anio in seleccionados:
    for mes, valores in zip(MESES, ventanas[anio]):
        filas.append({'anio': anio, 'mes': mes, **dict(zip(VARIABLES, valores))})
pd.DataFrame(filas).to_csv(SALIDA / '03_curvas_para_dashboard.csv', index=False, encoding='utf-8-sig')

# Figura principal: etiquetas claras y ejes separados para no mezclar magnitudes.
fig, axs = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
meses_txt = ['May', 'Jun', 'Jul', 'Ago', 'Sep']
for ax, (variable, titulo) in zip(axs, [('anom_nino12', 'Niño 1+2 · costa sudamericana'),
                                       ('anom_nino34', 'Niño 3.4 · Pacífico central')]):
    j = VARIABLES.index(variable)
    for anio in seleccionados[1:]:
        serie = ventanas[anio][:, j]
        ax.plot(MESES, serie, marker='o', linewidth=2, alpha=.75, label=str(anio))
        ax.annotate(str(anio), (9, serie[-1]), xytext=(7, 0), textcoords='offset points', fontsize=9)
    actual = ventanas[ANIO_OBJETIVO][:, j]
    ax.plot(MESES, actual, marker='o', linewidth=3.4, label=str(ANIO_OBJETIVO), color='black')
    ax.annotate('2026', (9, actual[-1]), xytext=(7, 0), textcoords='offset points', fontsize=10, weight='bold')
    ax.set_title(titulo, weight='bold')
    ax.set_xticks(MESES, meses_txt)
    ax.set_ylabel('Anomalía mensual (°C)')
    ax.grid(axis='y', alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
    ax.margins(x=.17)
fig.suptitle('ML 1 · ¿A qué año histórico se parece mayo–septiembre de 2026?', weight='bold', fontsize=14)
fig.savefig(SALIDA / '04_grafico_similitud.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print('\n=== ML 1: SIMILITUD HISTÓRICA ENSO ===')
print('Periodo comparado: mayo-septiembre, años históricos completos anteriores a 2026')
print('Años históricos candidatos:', len(anios_historicos))
print('\nCinco análogos más cercanos (modelo k-NN):')
print(resultado.head(5).to_string(index=False, float_format=lambda x: f'{x:.3f}'))
print('\nValidaciones retrospectivas:', len(validacion))
print('RMSE medio de los análogos históricos:', round(validacion.rmse_4_indices_c.mean(), 3) if len(validacion) else 'N/D')
print('\nResultados guardados en:', SALIDA)
print('IMPORTANTE: similitud histórica NO equivale a pronóstico de lluvias ni a predicción futura.')
