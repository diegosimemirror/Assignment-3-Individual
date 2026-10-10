"""Emergencias por lluvias: ejecutar con uv run streamlit run app.py."""
# Path construye rutas relativas a este archivo; json convierte mapas a GeoJSON.
from pathlib import Path
import json
from datetime import timedelta  # Define el paso diario del filtro.
import pandas as pd  # Lee y cruza tablas, como operaciones de Excel.
import geopandas as gpd  # Lee polígonos y transforma sus coordenadas.
import plotly.graph_objects as go  # Dibuja capas interactivas del mapa.
import streamlit as st  # Construye filtros, métricas y tabla de la aplicación.

st.set_page_config(page_title="Emergencias por lluvias en Perú", page_icon="🗺️", layout="wide")
CARPETA = Path(__file__).resolve().parent

# PROCESO 1: Archivos de entrada → tablas y geometrías en memoria.
# El cache evita volver a leer los archivos al cambiar las fechas.
@st.cache_data
def cargar_datos():
    normas = pd.read_excel(CARPETA / 'datos/scrapping_4_completo.xlsx', sheet_name=0,
                           dtype={'Ubigeo': str})
    normas.columns = normas.columns.str.strip()
    normas = normas.rename(columns={
        'Nombre del documento': 'norma',
        'Tipo de documento: Declaratoria / Prorroga': 'tipo',
        'Enlace web': 'enlace', 'Distrito': 'distrito', 'Provincia': 'provincia',
        'Departamento': 'departamento', 'Ubigeo': 'ubigeo',
        'Dia del inicio del estado de emergencia': 'inicio',
        'Dia del fin del estado de emergencia': 'fin'})
    normas['ubigeo'] = normas['ubigeo'].str.strip().str.zfill(6)
    for columna in ['inicio', 'fin']:
        normas[columna] = pd.to_datetime(normas[columna], errors='raise').dt.normalize()
    if (normas['fin'] < normas['inicio']).any():
        raise ValueError('Hay vigencias cuyo fin precede al inicio.')
    if normas.duplicated(['norma', 'ubigeo']).any():
        raise ValueError('Hay registros duplicados de norma y distrito.')
    # Los primeros 2 y 4 caracteres identifican departamento y provincia.
    normas['codigo_departamento'] = normas['ubigeo'].str[:2]
    normas['codigo_provincia'] = normas['ubigeo'].str[:4]
    lluvia = pd.read_csv(CARPETA / 'datos/dataset.csv', dtype={'ubigeo': str})
    lluvia['codigo_departamento'] = lluvia['ubigeo'].str.strip().str.zfill(2)
    # Cruce muchos-a-uno: repetir el contexto de la capital no duplica las normas.
    normas = normas.merge(lluvia[['codigo_departamento', 'capital', 'lluvia_total_mm']],
                          on='codigo_departamento', how='left', validate='many_to_one')
    capas = {}
    for nivel in ['distritales', 'provinciales', 'departamentales']:
        archivos = list((CARPETA / 'datos' / f'limites_{nivel}').glob('*.shp'))
        if len(archivos) != 1:
            raise ValueError(f'Debe existir un solo shapefile en limites_{nivel}.')
        capa = gpd.read_file(archivos[0]).to_crs(4326)
        # Reducir columnas conserva geometrías y nombres necesarios.
        if nivel == 'distritales':
            capa = capa.rename(columns={'UBIGEO': 'ubigeo', 'DISTRITO': 'distrito',
                'PROVINCIA': 'provincia', 'DEPARTAMEN': 'departamento'})
            capa['ubigeo'] = capa['ubigeo'].astype(str).str.zfill(6)
            capa = capa[['ubigeo', 'distrito', 'provincia', 'departamento', 'geometry']]
            if capa['ubigeo'].duplicated().any():
                raise ValueError('El mapa contiene ubigeos duplicados.')
        else:
            capa = capa[['geometry']]
        # Simplificación SOLO visual: no altera códigos, registros ni conteos.
        capa['geometry'] = capa.geometry.simplify(0.001, preserve_topology=True)
        capas[nivel] = capa
    return normas, capas

# PROCESO 2: Polígonos → coordenadas de contornos provinciales/departamentales.
def agregar_contornos(figura, capa, nombre, color, grosor):
    longitudes, latitudes = [], []
    for geometria in capa.geometry:
        if geometria is None or geometria.is_empty:
            continue
        poligonos = list(geometria.geoms) if geometria.geom_type == 'MultiPolygon' else [geometria]
        for poligono in poligonos:
            x, y = poligono.exterior.xy
            longitudes.extend(list(x) + [None])
            latitudes.extend(list(y) + [None])
    figura.add_trace(go.Scattermap(lon=longitudes, lat=latitudes, mode='lines',
        line={'color': color, 'width': grosor}, name=nombre, hoverinfo='skip', showlegend=False))

try:
    normas, capas = cargar_datos()
except (ValueError, FileNotFoundError) as error:
    st.error(str(error))
    st.stop()

# PROCESO 3: Intervalo elegido → normas con al menos un día de coincidencia.
minimo, maximo = normas['inicio'].min().date(), normas['fin'].max().date()
st.sidebar.header('Periodo de vigencia')
inicio, fin = st.sidebar.slider('Seleccione fecha inicial y final', min_value=minimo,
    max_value=maximo, value=(minimo, minimo), step=timedelta(days=1), format='DD/MM/YYYY')
st.sidebar.caption('Para consultar un solo día, coloque ambos extremos en la misma fecha.')
filtrado = normas[(normas['inicio'] <= pd.Timestamp(fin)) &
                  (normas['fin'] >= pd.Timestamp(inicio))].copy()
st.title('Distritos bajo emergencia por lluvias')
st.caption('Consulta de 20 decretos de 2024: declaratorias y prórrogas incluidas en la base.')
if inicio == fin:
    titulo = f'Distritos bajo emergencia el {inicio:%d/%m/%Y}'
else:
    titulo = f'Distritos con emergencia vigente al menos un día entre el {inicio:%d/%m/%Y} y el {fin:%d/%m/%Y}'
st.write(titulo)

# PROCESO 4: Registros filtrados → conteos y porcentajes de territorios distintos.
# El total de referencia sale del mapa completo, no de la base de decretos.
codigos_mapa = capas['distritales']['ubigeo']
total_departamentos = codigos_mapa.str[:2].nunique()  # Incluye Callao.
total_provincias = codigos_mapa.str[:4].nunique()
total_distritos = codigos_mapa.nunique()

# Contar códigos únicos evita duplicar lugares con varias normas o prórrogas.
departamentos_emergencia = filtrado['codigo_departamento'].nunique()
provincias_emergencia = filtrado['codigo_provincia'].nunique()
distritos_emergencia = filtrado['ubigeo'].nunique()

# Mostrar el porcentaje debajo del conteo, sin flechas de variación.
a, b, c = st.columns(3)
indicadores = [
    (a, 'Departamentos', departamentos_emergencia, total_departamentos,
     'unidades departamentales'),
    (b, 'Provincias', provincias_emergencia, total_provincias, 'provincias'),
    (c, 'Distritos', distritos_emergencia, total_distritos, 'distritos'),
]
for columna, etiqueta, cantidad, total, unidad in indicadores:
    columna.metric(etiqueta, cantidad)
    # Proteger el cálculo si una cartografía no contiene códigos válidos.
    if total > 0:
        porcentaje = cantidad / total * 100
        texto_porcentaje = f'{porcentaje:.1f}'.replace('.', ',')
        texto_total = f'{total:,}'.replace(',', '.')
        columna.caption(f'{texto_porcentaje} % del total de {texto_total} {unidad}')
    else:
        columna.caption('Total de referencia no disponible')

st.caption(
    'Porcentajes respecto de los territorios de la cartografía utilizada. '
    'El nivel departamental incluye los 24 departamentos y Callao. '
    'Se cuentan lugares con alguna emergencia vigente durante el intervalo, '
    'según los decretos incluidos en la base; sus vigencias pueden corresponder '
    'a fechas diferentes dentro de ese intervalo.'
)

# PROCESO 5: Ubigeos filtrados → mapa con distritos de un mismo color.
st.subheader('Alcance territorial de las emergencias')
distritos = capas['distritales']
seleccionados = distritos[distritos.ubigeo.isin(filtrado.ubigeo)]
sin_mapa = filtrado[~filtrado.ubigeo.isin(distritos.ubigeo)]
if not sin_mapa.empty:
    st.warning(f'{sin_mapa.ubigeo.nunique()} distritos seleccionados no tienen geometría; sí están incluidos en métricas y tabla.')
if filtrado.empty:
    st.info('No hay normas vigentes en este periodo dentro de la base consultada.')
figura = go.Figure()
# Fondo nacional gris con nombres disponibles al pasar el cursor.
for capa, color, nombre in [(distritos, '#edf0f2', 'Distritos'),
                          (seleccionados, '#267baf', 'Con emergencia')]:
    if capa.empty:
        continue
    figura.add_trace(go.Choroplethmap(
        geojson=json.loads(capa.to_json()), featureidkey='properties.ubigeo',
        locations=capa.ubigeo, z=[1]*len(capa), zmin=0, zmax=1,
        colorscale=[[0, color], [1, color]], showscale=False,
        marker_line_width=0.3, marker_line_color='#ffffff',
        customdata=capa[['distrito','provincia','departamento']].to_numpy(),
        hovertemplate='<b>%{customdata[0]}</b><br>Provincia: %{customdata[1]}<br>Departamento: %{customdata[2]}<extra>'+nombre+'</extra>',
        name=nombre))
agregar_contornos(figura, capas['provinciales'], 'Provincias', '#7e8891', 0.6)
agregar_contornos(figura, capas['departamentales'], 'Departamentos', '#34424d', 1.4)
figura.update_layout(map={'style':'white-bg','center':{'lat':-9.2,'lon':-75.0},'zoom':4},
    height=650, margin={'l':0,'r':0,'t':0,'b':0})
st.plotly_chart(figura, width='stretch')
st.caption('Azul: emergencia según las normas consultadas. Gris: sin coincidencia en esta base; no implica ausencia de otras emergencias.')

# PROCESO 6: Normas filtradas → detalle y CSV descargable.
st.subheader('Declaratorias y prórrogas que coinciden con el periodo')
st.caption('La lluvia es una referencia fija de la capital departamental, del 01/01 al 31/05/2024; no corresponde al intervalo del filtro ni a cada distrito.')
tabla = filtrado.sort_values(['departamento','provincia','distrito','inicio'])[
    ['norma','tipo','distrito','provincia','departamento','lluvia_total_mm','capital','inicio','fin','ubigeo','enlace']].copy()
for columna in ['inicio','fin']:
    tabla[columna] = tabla[columna].dt.strftime('%d/%m/%Y')
tabla = tabla.rename(columns={'norma':'Decreto','tipo':'Tipo','distrito':'Distrito',
    'provincia':'Provincia','departamento':'Departamento','capital':'Capital departamental',
    'lluvia_total_mm':'Lluvia en capital ene–may 2024 (mm)','inicio':'Inicio de vigencia',
    'fin':'Fin de vigencia','ubigeo':'Ubigeo','enlace':'Fuente'})
st.dataframe(tabla, hide_index=True, width='stretch',
    column_config={'Fuente':st.column_config.LinkColumn('Fuente', display_text='Ver norma'),
        'Lluvia en capital ene–may 2024 (mm)':st.column_config.NumberColumn(format='%.1f')})
st.download_button('Descargar tabla filtrada (CSV)', tabla.to_csv(index=False).encode('utf-8-sig'),
    file_name=f'emergencias_{inicio}_{fin}.csv', mime='text/csv')
with st.expander('Fuentes y criterio de consulta'):
    st.write('Las fechas inicial y final se incluyen. Cada fila es una norma y un distrito; cada territorio se cuenta una sola vez. En intervalos de varios días, los distritos pueden haber tenido vigencias en fechas diferentes.')
    st.write('Fuentes: compilación de decretos PCM con enlaces oficiales; cartografía INEI distribuida por Geo GPS Perú; acumulados meteorológicos de Open-Meteo preparados en dataset.csv. La cobertura se limita a las normas incluidas, no a todas las emergencias del país.')
    st.write('La lluvia repetida en filas del mismo departamento no debe sumarse. La cartografía más reciente se emplea para representar normas de 2024; no reconstruye límites históricos.')
