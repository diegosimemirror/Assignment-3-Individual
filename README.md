# Distritos bajo emergencia por lluvias en Perú

Aplicación Streamlit adaptada a la arquitectura de la sesión 8: carga con caché, filtro lateral, métricas, mapa interactivo de Plotly y tabla descargable.

## Sobre el dashboard

Este dashboard busca que un tomador de decisión pueda obtener, **en un vistazo de dos minutos**, una dimensión del alcance territorial de las declaratorias y prórrogas de emergencia: cuántos territorios están comprendidos, dónde se encuentran y qué normas sustentan su inclusión.

Esta información puede servir como punto de partida para orientar la coordinación con gobiernos regionales y autoridades locales durante y después de la emergencia, así como para organizar consultas sobre qué se hizo gracias al estado de emergencia, qué falta hacer y qué se debe regularizar posteriormente.

### 1. Elegir un intervalo de vigencia

El dashboard permite elegir una fecha de inicio y una fecha de fin. A partir de esa selección, filtra las declaratorias y prórrogas de emergencia que estuvieron **vigentes por lo menos un día dentro del intervalo**. Al seleccionar la misma fecha en ambos extremos, se consulta un solo día.

Esta precisión es importante: si se elige un intervalo de varios días, una emergencia puede haber estado activa solamente durante una parte de ese periodo. Por ello, los territorios mostrados no necesariamente estuvieron en emergencia durante todos los días ni de manera simultánea.

La base comprende **20 decretos de 2024**, con vigencias entre el **27 de enero y el 6 de julio de 2024**. La consulta se limita a los decretos incluidos en la base; no constituye un inventario exhaustivo de las emergencias del país.

### 2. Dimensionar la coordinación territorial

Al seleccionar el intervalo, el dashboard presenta tres métricas clave: el número de **departamentos, provincias y distritos** comprendidos, junto con el porcentaje que representan respecto del total de territorios de la cartografía utilizada.

Estos indicadores permiten dimensionar el involucramiento territorial de los estados de emergencia y lo que puede implicar la coordinación con gobiernos regionales y autoridades locales. Cada territorio se cuenta una sola vez, aunque tenga varias declaratorias o prórrogas dentro del intervalo. Los conteos corresponden a territorios únicos, no al número de filas.

Los totales de referencia se calculan a partir de los códigos únicos de la capa distrital utilizada. Esta cartografía contiene 25 unidades de nivel departamental, 196 provincias y 1.892 distritos. El nivel departamental incluye los 24 departamentos y la Provincia Constitucional del Callao. Estos totales corresponden a la cartografía utilizada, no a una reconstrucción de la división territorial histórica de 2024.

### 3. Visualizar los distritos en el mapa

El mapa interactivo muestra en azul oscuro los distritos comprendidos por las declaratorias o prórrogas que coinciden con el intervalo seleccionado.

Al pasar el mouse sobre un distrito, aparecen su nombre, el de su provincia y el de su departamento. Esto facilita una lectura territorial conjunta del alcance de las emergencias y permite ubicar las zonas sobre las cuales orientar las coordinaciones.

El fondo gris identifica distritos sin coincidencia en la base consultada para el intervalo seleccionado; no implica ausencia de otras emergencias.

### 4. Consultar y descargar el detalle para el seguimiento

El dashboard genera una lista de los distritos comprendidos, indicando la declaratoria o prórroga correspondiente, su vigencia, la provincia y el departamento. También permite acceder a la normativa sustentatoria mediante enlaces y descargar la lista filtrada en formato CSV. Cada fila corresponde a una norma y un distrito; un distrito puede aparecer en varias filas si tiene distintas normas dentro del intervalo.

Como dato **solo referencial**, la tabla incluye el acumulado de precipitaciones de enero a mayo de 2024, tomando como punto de referencia la capital del departamento. Este valor ofrece una aproximación al contexto de lluvias en la capital; no representa la precipitación de cada distrito ni cambia con el intervalo seleccionado.

La lista puede servir como punto de partida para tomar contacto con autoridades o coordinadores, distribuir coordinaciones y asignar puntos focales para la ayuda a las zonas afectadas. También facilita organizar el seguimiento: conocer qué se hizo, evaluar si las medidas adoptadas durante el estado de emergencia sirvieron e identificar qué queda por hacer y cuál es la situación actual una vez pasada la emergencia. La aplicación no contiene resultados de ese seguimiento ni evalúa por sí misma la efectividad de las medidas.

### Hallazgos

Hallazgo 1. 

Al consultar todo el periodo disponible, del 27 de enero al 6 de julio de 2024, los decretos incluidos comprendieron 873 distritos de 159 provincias y 24 unidades de nivel departamental, equivalentes al 46,1 %, 81,1 % y 96,0 % de los territorios de la cartografía utilizada. Estas vigencias no necesariamente fueron simultáneas.

Hallazgo 2. Pocas normas pueden comprender un despliegue territorial amplio y disperso

Los 20 decretos de declaratoria y prórroga incluidos en la base, que pueden parecer pocos al revisar únicamente el listado normativo, comprendieron 873 distritos durante el periodo analizado. Su alcance está disperso tanto en el espacio como en el tiempo: las vigencias corresponden a distintos intervalos y no necesariamente coinciden entre los territorios.

Este fue un aprendizaje central del trabajo: la normativa, presentada mediante decretos y tablas de lugares que requieren incorporar el UBIGEO para su análisis, necesita también una lectura desde los datos. Revisar cada decreto por separado dificulta mantener una visión de conjunto del país y dimensionar la coordinación territorial que implica lo declarado en emergencia.

El dashboard complementa el enfoque legal de la publicación de las normas con una mirada territorial: permite visualizar dónde se despliegan sus efectos, cuándo coinciden sus vigencias y cuántos territorios están comprendidos. Esa visión puede orientar coordinaciones y preguntas de seguimiento sobre lugares con realidades climáticas y de infraestructura diferentes, aunque esas diferencias no se midan directamente en esta aplicación.

## Archivos y fuentes

- `datos/scrapping_4_completo.xlsx`: compilación de 20 decretos PCM de 2024, con enlaces oficiales y vigencias. No es un inventario exhaustivo nacional. Para este ejercicio se preparó la base con ayuda de Claude Code; las fuentes normativas originales están enlazadas en cada registro.
- `datos/dataset.csv`: precipitación acumulada de [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), asociada a capitales departamentales, del 1 de enero al 31 de mayo de 2024. Es fija y referencial: no representa lluvia distrital ni lluvia del periodo filtrado.
- `datos/limites_distritales/`: capa suministrada como **Mapa Población Distrital Censo 2025**, con cartografía atribuida a INEI y distribuida por [Geo GPS Perú](https://www.geogpsperu.com/2026/07/mapa-poblacion-distrital-censo-2025.html). Se utilizan los códigos, nombres y geometrías territoriales; no se usan las cifras poblacionales.
- `datos/limites_provinciales/` y `datos/limites_departamentales/`: contornos suministrados de INEI/Geo GPS Perú. Véase el [sitio de distribución cartográfica](https://www.geogpsperu.com/).

Conserve juntos los componentes de cada shapefile, especialmente `.shp`, `.shx`, `.dbf` y `.prj`. No sume la precipitación repetida por distrito o decreto. Los límites recientes no reconstruyen la división territorial histórica de 2024.

## Ejecución local

Con el entorno virtual activado, desde la carpeta que contiene `app.py`, `requirements.txt` y `datos/`, instale las dependencias y ejecute la aplicación:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Si el entorno fue creado con `uv` y no dispone de `pip`, puede instalar las dependencias con `uv pip install -r requirements.txt` y luego ejecutar `python -m streamlit run app.py`.

Abra en el navegador la dirección local indicada en la terminal. Para detener la aplicación, presione `Ctrl+C` en esa terminal.

## Publicación

Suba `app.py`, `requirements.txt`, `README.md` y la carpeta `datos/` al repositorio de GitHub. Mantenga `requirements.txt` junto a `app.py`.

En [Streamlit Community Cloud](https://share.streamlit.io/), seleccione el repositorio, la rama y la ruta de `app.py`. Si está dentro de `assignment_3/`, la ruta será `assignment_3/app.py`.

Tras desplegar, compruebe que el filtro actualice las métricas y el mapa, que los nombres territoriales aparezcan al pasar el mouse y que la descarga CSV corresponda al intervalo seleccionado.

**Enlace público:** pendiente de despliegue. Reemplazar esta línea por la URL real de la aplicación.

## Procesos

1. Cargar las tablas, acortar encabezados y cruzar la lluvia por código departamental.
2. Convertir los contornos a coordenadas para dibujar líneas.
3. Filtrar las normas con `inicio_norma <= fin_elegido` y `fin_norma >= inicio_elegido`, incluyendo ambos extremos.
4. Contar departamentos, provincias y distritos únicos por UBIGEO y calcular sus porcentajes respecto de los totales de la cartografía utilizada.
5. Representar los distritos seleccionados en azul sobre un fondo nacional gris.
6. Mostrar una fila por norma y distrito y ofrecer la descarga CSV.

El filtro selecciona registros para la vista sin modificar la base original. Las geometrías se simplifican únicamente para la visualización y la velocidad de carga; esto no modifica los códigos ni los conteos territoriales.
