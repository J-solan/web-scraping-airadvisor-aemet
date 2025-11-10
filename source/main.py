from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from bs4 import BeautifulSoup

from selenium_interaction import selenium_interact, set_navigator
from wscrapping_aemet import return_airport, extract_stats

import argparse
import re
from datetime import datetime, timedelta
import pandas as pd
import time

def merge_weather_flights(df_weather, df_flights):
    
    df_weather['Día'] = df_weather['Día'].astype(str)
    df_flights['Fecha'] = df_flights['Fecha'].astype(str)
    
    # Hacer el inner join
    df_merged = pd.merge(
        df_flights,
        df_weather,
        left_on='Fecha',
        right_on='Día',
        how='inner'
    )
    
    # Eliminar la columna duplicada 'Día' ya que tenemos 'Fecha'
    if 'Día' in df_merged.columns:
        df_merged = df_merged.drop('Día', axis=1)
    
    # Reordenar columnas para mejor legibilidad (fecha y hora primero, luego vuelo, luego clima)
    cols = df_merged.columns.tolist()
    priority_cols = ['Fecha', 'Hora', 'Aerolínea y vuelo', 'Origen', 'Destino', 'Estado']
    other_cols = [col for col in cols if col not in priority_cols]
    df_merged = df_merged[priority_cols + other_cols]
    
    return df_merged

def clean_last_week_data(df):
    # Para quedarnos solo con datos de la última semana como en aemet
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
    
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calcular rango: desde hace 7 días hasta hoy
    fecha_fin = hoy  # Hoy
    fecha_inicio = hoy - timedelta(days=7)  # Hace 7 días
    
    # Filtrar el DataFrame
    df_filtrado = df[(df['Fecha'] >= fecha_inicio) & (df['Fecha'] <= fecha_fin)].copy()
    df_filtrado['Fecha'] = df_filtrado['Fecha'].dt.strftime('%d/%m/%Y')
    
    return df_filtrado

def wscrapping(ciudad_destino, test, headless, verbose):
    verbose_result = []
    try:
        driver = set_navigator(headless)
        resultado = selenium_interact(driver, ciudad_destino)

        verbose_result.append("\nProcediendo a la extracción de datos...")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Localizar la tabla principal
        tabla = soup.find("div", class_="flight_table")

        # Extraemos todas las filas del html
        filas = tabla.find_all("div", class_="flight_table_row flight_table_elem")

        verbose_result.append(f"Filas encontradas: {len(filas)}")

        # Proceso de web scrapping con BeautifulSoup
        all_flights = []

        # Búsqueda del número de páginas a procesar
        try:
            paginacion = driver.find_element(By.CLASS_NAME, "flight_table_pagination")
            enlaces = paginacion.find_elements(By.CSS_SELECTOR, "ul.flight_table_pagination_ul a[data-page]")
            total_paginas = int(enlaces[-1].get_attribute("data-page")) if enlaces else 1
            verbose_result.append(f"Total de páginas encontradas: {total_paginas}")
        except NoSuchElementException:
            verbose_result.append("No se encontró la paginación, se asumirá una sola página.")
            total_paginas = 1

        # Recorrer las páginas
        for pagina in range(1, total_paginas + 1):
            verbose_result.append(f"\nProcesando página {pagina}...")
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tabla = soup.find("div", class_="flight_table")
            filas = tabla.find_all("div", class_="flight_table_row flight_table_elem") if tabla else []
            verbose_result.append(f"Filas encontradas: {len(filas)}")

            for fila in filas:
                fecha = fila.find("div", class_="flight_table_date")
                aerolinea = fila.find("span", class_="flight_table_airline")
                ruta = fila.find("ul", class_="flight_table_route")
                estado = fila.find("span", class_="flight_table_status")

                origen, destino = "", ""
                if ruta:
                    li_items = ruta.find_all("li")
                    if len(li_items) >= 2:
                        origen = li_items[0].get_text(strip=True)
                        destino = li_items[1].get_text(strip=True)

                # --- Separar fecha y hora ---
                fecha_text = fecha.get_text(strip=True) if fecha else ""
                match = re.match(r"(\d{2}\.\d{2}\.\d{4})(\d{2}:\d{2})", fecha_text)
                if match:
                    fecha_str, hora_str = match.groups()
                    # Convertir al formato deseado
                    fecha_formateada = datetime.strptime(fecha_str, "%d.%m.%Y").strftime("%d/%m/%Y")
                else:
                    fecha_formateada, hora_str = "", ""

                all_flights.append({
                    "Fecha": fecha_formateada,
                    "Hora": hora_str,
                    "Aerolínea y vuelo": aerolinea.get_text(strip=True) if aerolinea else "",
                    "Origen": origen,
                    "Destino": destino,
                    "Estado": estado.get_text(strip=True) if estado else ""
                })

            # Si solo hay una página cerramos el proceso directamente
            if total_paginas == 1:
                verbose_result.append("Sólo había una página, finalizando...")
                break

            # Pasamos la página
            if pagina < total_paginas:
                # Cerrar popup si aparece
                try:
                    boton_cerrar_popup = driver.find_element(By.CLASS_NAME, "close-claim-info")
                    driver.execute_script("arguments[0].click();", boton_cerrar_popup)
                    time.sleep(0.5)
                    verbose_result.append("Popup cerrado")
                except NoSuchElementException:
                    pass
                
                # Pasar la página
                try:
                    boton_siguiente = driver.find_element(By.XPATH, "//div[@class='flight_table_pagination']/a[@data-page]")
                    boton_siguiente.click()
                    time.sleep(2)
                except NoSuchElementException:
                    verbose_result.append("No se encontró el botón de siguiente página, finalizando...")
                    break

            # # Cerrar navegador al terminar
            driver.quit()
            verbose_result.append("Navegador cerrado")

    except Exception as e:
        print("Error:", e)

    if all_flights:
        # Guardar resultados
        df_flights = pd.DataFrame(all_flights)
        verbose_result.append(f"Buscando estación meterorológica de {ciudad_destino}")
        airport = return_airport(ciudad_destino)
        verbose_result.append("Estación encontrada")
        df_weather = extract_stats(airport["value"])
        df = merge_weather_flights(df_weather, df_flights)
        if not test:
            file_name = f"airadvisor_{ciudad_destino}.csv"
            df.to_csv(f"data/{file_name}", index=False, encoding="utf-8-sig")
        if verbose:
            for linea in verbose_result:
                print(linea)
        return df

if __name__ == "__main__":

    ## Configuración del parser de argumentos ##
    parser = argparse.ArgumentParser(
        description="Descarga información de vuelos de una ciudad destino específica."
    )

    parser.add_argument(
        "--test",
        action="store_true",              # convierte el flag en True si se pasa
        required=False,                   # no es obligatorio
        default=False,                     # valor por defecto
        help="Ejecutar en modo test"
    )

    parser.add_argument(
        "--ciudad",
        type=str,
        required=False,  # obliga a pasar el argumento
        help="Nombre de la ciudad destino (por ejemplo: Sevilla)"
    )

    parser.add_argument(
        "--headless",
        action="store_true",              # convierte el flag en True si se pasa
        required=False,                   # no es obligatorio
        default=False,                     # valor por defecto
        help="Ejecutar el navegador en modo headless (sin interfaz gráfica)."
    )

    parser.add_argument(
        "--verbose",
        action="store_true",              # convierte el flag en True si se pasa
        required=False,                   # no es obligatorio
        default=False,                    # valor por defecto
        help="Mostrar el verbose para ver qué va haciendo el webscrapping."
    )

    args = parser.parse_args()

    test = args.test
    ciudad_destino = args.ciudad
    headless= args.headless
    verbose = args.verbose

    ciudades = ["Madrid", "Barcelona", "Mallorca", "Málaga", "Alicante", "Canaria", "Tenerife", "Ibiza", "Lanzarote", "Valencia"]
    ## ------------------------------------ ##

    if test:
        dfs = []
        for ciudad in ciudades:
            df_ciudad = wscrapping(ciudad, test, headless, verbose)
            dfs.append(df_ciudad)
        df = pd.concat(dfs, ignore_index=True)
        ruta_salida = "dataset/dataset.csv"
        df.to_csv(ruta_salida, index=False, encoding="utf-8")
    else:
        # Solo crea un csv con la ciudad indicada
        wscrapping(ciudad_destino, test, headless, verbose)
