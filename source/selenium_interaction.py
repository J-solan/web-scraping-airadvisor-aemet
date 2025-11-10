# Librerias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

import time

URL = "https://airadvisor.com/es/vuelos"

# Configuración del navegador

def set_navigator(headless):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    print("Navegador iniciado")

    return driver

def abrir_pagina(driver):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Entramos en la web
        driver.get(URL)
        time.sleep(2)

        print("Página abierta con éxito")
        
        # Rechazo las cookies porque no quiero que se queden con mis datos
        try:
            cookies_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookiescript_reject")))
            cookies_btn.click()
            print("Cookies rechazadas")
            time.sleep(1)

        except TimeoutException:
            print("No se encontró banner de cookies")
        
        return True
        
    # Aunque sé que funciona añado manejo de excepciones por si acaso
    except Exception as e:
        print(f"Error: {e}")
        return False

# Quiero poder seleccionar una ciudad como destino
def seleccionar_destino(driver, ciudad_destino):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Encontrar input de destino
        input_destino = driver.find_element(By.XPATH, "//input[@placeholder='Aeropuerto de destino final']")
        
        # Escribir ciudad destino
        input_destino.clear()
        input_destino.send_keys(ciudad_destino)
        print(f"Destino: {ciudad_destino}")
        
        time.sleep(2)
        
        # Seleccionar primera opción
        try:
            primera_opcion = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-results__option:first-child"))
            )
            primera_opcion.click()
            print(f"{ciudad_destino} seleccionada como destino")

        except TimeoutException:
            input_destino.send_keys(Keys.ENTER)
            print(f"{ciudad_destino} confirmada como destino")
        
        time.sleep(1)
        return True
        
    except Exception as e:
        print(f"Error seleccionando {ciudad_destino} como destino: {e}")
        return False
    
def hacer_busqueda(driver):
    # Esperas para la tabla y el botón de búsqueda
    wait_corto = WebDriverWait(driver, 5)
    wait_largo = WebDriverWait(driver, 15)  # Más tiempo para resultados
    
    try:
        # Encontrar botón de búsqueda
        boton = wait_corto.until(EC.element_to_be_clickable((By.ID, "fcCheckFlight")))
        
        # Scroll para que esté visible en el centro
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
        time.sleep(0.5)
        
        try:
            # Hacer click para buscar
            boton.click()
            
            print("Búsqueda realizada con éxito")

            # Intentar buscar tabla primero
            wait_largo.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print("Tabla de resultados encontrada")
            return True
        
        except Exception as e:
            print(f"Error buscando tabla: {e}")
            return False
    
    except Exception as e:
            print(f"Error intentando realizar búsqueda: {e}")
            return False

def selenium_interact(driver, ciudad_destino):
    print(f"Buscando vuelos hacia {ciudad_destino}")
    print("-" * 40)

    abrir_pagina(driver=driver)

    seleccionar_destino(driver=driver, ciudad_destino=ciudad_destino)

    hacer_busqueda(driver=driver)
