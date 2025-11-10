# Cancelación y retraso de vuelos en los aeropuertos españoles más importantes en relación con el clima.

**Autores:** Jorge Solán Morote y Javier Solís Ron 
**Asignatura:** Tipología y ciclo de vida de los datos  
**Máster:** Data Science, UOC  
**Práctica:** 1  

---

## Descripción

Este proyecto tiene como objetivo extraer y combinar información sobre **retrasos y cancelaciones de vuelos** en España con **datos climáticos** de las estaciones meteorológicas de los aeropuertos correspondientes. El flujo general del proyecto es:

1. Extracción de un dataset con registros de **retrasos y cancelaciones de vuelos** con destino en distintos aeropuertos de España.
2. Extracción de un dataset con **datos climáticos** de las estaciones meteorológicas asociadas a esos aeropuertos, incluyendo precipitaciones, temperaturas y rachas de viento.
3. **Fusión de ambos datasets** según ciudad de destino y estación, y fecha del vuelo y medición meteorológica, generando un dataset final más completo.

---

## Estructura del proyecto

main/
├─ data/ # Carpeta donde se guardan los datasets generados (vacía inicialmente)
├─ dataset/
│ └─ dataset.csv # Archivo con el dataset final de ejemplo
├─ source/
│ ├─ main.py # Script principal de ejecución con el scraping de vuelos y la fusión con AEMET.
│ ├─ dataset_concat.py # Script para fusionar los datasets
│ ├─ selenium_interaction.py # Funciones de interacción con Selenium
│ └─ wscrapping_aemet.py # Scraping de datos meteorológicos de AEMET
├─ requirements.txt # Librerías necesarias para ejecutar el proyecto

---

## Uso

El script principal es `main.py`, que permite generar datasets de vuelos con datos climáticos.

**Opciones de ejecución:**

- `--ciudad <nombre_ciudad>`  
  Extrae el dataset de vuelos y clima para la ciudad indicada. El dataset se guarda en `data/`.

- `--verbose`  
  Muestra información adicional durante la ejecución.

- `--headless`  
  Ejecuta Selenium en modo headless (sin abrir la ventana del navegador).

- `--test`  
  Genera un dataset de prueba con 10 ciudades incluidas en el programa. Se guarda como `/dataset/dataset.csv`.

**Fusionar datasets:**

Ejecutar `dataset_concat.py` permite combinar todos los datasets almacenados en `data/`.  
Parámetros principales:

- `--out <nombre_archivo>`  
  Nombre del archivo de salida fusionado, que se guarda en la carpeta `dataset/`.

---

## Ejemplos de uso

**Generar dataset de vuelos y clima para una ciudad específica:**
```
python source/main.py --ciudad Madrid
```

**Generar dataset de prueba con 10 ciudades:**
```
python source/main.py --test
```

**Ejecutar scraping en modo headless y con información detallada:**
```
python source/main.py --ciudad Barcelona --headless --verbose
```

**Fusionar datasets guardados en data/ y guardar el resultado en dataset/final.csv:**
```
python source/dataset_concat.py --out final.cs
```
---

## Zenodo
Además de este repositorio se ha compartido el dataset obtenido en la plataforma Zenodo, el DOI de dicha web para nuestro dataset es:  10.5281/zenodo.17575816