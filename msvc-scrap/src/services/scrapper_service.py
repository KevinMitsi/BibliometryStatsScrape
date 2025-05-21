import os
import time
import shutil
import glob
import json
import hashlib
import xml.etree.ElementTree as ET

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

XML_PATH = "//input[@data-auto='bulk-download-formats-group-input' and @value='xml']"
BTN_PATH = "//button/span[text()='Siguiente']/parent::button"

# Constantes de URLs
BASE_URL = "https://research-ebsco-com.crai.referencistas.com"
SEARCH_URL_TEMPLATE = BASE_URL + "/c/q46rpe/search/results?limiters=&q={query}"

# Selectors
SEARCH_BOX_ID = "search-input"
RESULT_LIST_ID = "result-list"
ARTICLE_WRAPPER_CLASS = "search-result-item_search-result-item__wrapper___EVmK"
LOAD_MORE_BUTTON = "//button[@data-auto='show-more-button' and contains(text(), 'Mostrar más resultados')]"


def setup_driver(browser_path, download_dir, headless=False ):
    options = Options()
    options.binary_location = browser_path
    # Descargas automáticas
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "plugins.always_open_pdf_externally": True,
        "browser.helperApps.neverAsk.saveToDisk": "application/x-research-info-systems,application/xml,text/xml"
    }
    options.add_experimental_option("prefs", prefs)
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": download_dir}
    )
    driver.maximize_window()  # Maximizar ventana para evitar problemas con elementos no visibles
    return driver


def log_into_library(driver, user, key):
    driver.get(BASE_URL)
    btn_google = WebDriverWait(driver, 15).until(
        ec.element_to_be_clickable((By.ID, "btn-google"))
    )
    btn_google.click()
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
    # Email
    WebDriverWait(driver, 15).until(
        ec.presence_of_element_located((By.ID, "identifierId"))
    ).send_keys(user)
    WebDriverWait(driver, 15).until(
        ec.element_to_be_clickable((By.XPATH, BTN_PATH))
    ).click()
    # Password
    WebDriverWait(driver, 15).until(
        ec.presence_of_element_located((By.NAME, "Passwd"))
    ).send_keys(key)
    WebDriverWait(driver, 15).until(
        ec.element_to_be_clickable((By.XPATH, "//span[text()='Siguiente']/.."))
    ).click()
    # Esperar a que la página se cargue completamente después del login
    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.ID, SEARCH_BOX_ID))
    )
    print("Login completado.")


def get_article_title(driver, idx):
    """Obtiene el título del artículo para usarlo en el nombre del archivo"""
    try:
        title_xpath = f"//div[@id='record-{idx}-detail']/div/h2/a"
        title_element = WebDriverWait(driver, 3).until(
            ec.presence_of_element_located((By.XPATH, title_xpath))
        )
        title = title_element.text.strip()
        # Limitar longitud y eliminar caracteres problemáticos para nombres de archivo
        safe_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in title)
        safe_title = safe_title[:50]  # Limitar a 50 caracteres para evitar nombres muy largos
        return safe_title
    except:
        return f"article_{idx}"  # Nombre genérico si no se puede obtener el título


def wait_for_download_complete(download_dir, timeout=30):
    """Espera a que la descarga se complete verificando archivos .crdownload o .tmp"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Verificar si hay archivos en proceso de descarga
        if not glob.glob(os.path.join(download_dir, "*.crdownload")) and \
                not glob.glob(os.path.join(download_dir, "*.tmp")):
            # Verificar si se descargó algún archivo XML
            if glob.glob(os.path.join(download_dir, "*.xml")):
                time.sleep(1)  # Esperar un poco más para asegurarse
                return True
        time.sleep(0.5)
    return False


def rename_last_downloaded_file(download_dir, new_name):
    """Renombra el archivo más reciente descargado y verifica si es duplicado"""
    # Obtener todos los archivos XML en el directorio
    xml_files = glob.glob(os.path.join(download_dir, "*.xml"))
    if not xml_files:
        return False

    # Ordenar por tiempo de modificación (el más reciente al final)
    latest_file = max(xml_files, key=os.path.getmtime)

    # Crear un nombre único con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{new_name}_{timestamp}.xml"
    new_path = os.path.join(download_dir, new_filename)

    # Renombrar el archivo
    try:
        shutil.move(latest_file, new_path)
        print(f"Archivo renombrado: {new_filename}")

        # Verificar si es duplicado
        is_duplicate = check_and_handle_duplicate(download_dir, new_path)

        # Si es duplicado, retornar False para no contarlo como descarga exitosa
        return not is_duplicate
    except Exception as e:
        print(f"Error al renombrar archivo: {str(e)}")
        return False


def load_more_results(driver):
    """Hace clic en el botón 'Mostrar más resultados' si está presente"""
    try:
        # Verificar si el botón está visible
        load_more_btn = WebDriverWait(driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, LOAD_MORE_BUTTON))
        )

        # Desplazarse hasta el botón para asegurarse de que sea visible
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
        time.sleep(3)

        # Hacer clic en el botón
        driver.execute_script("arguments[0].click();", load_more_btn)

        # Esperar a que se carguen más resultados
        time.sleep(10)
        return True
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        # El botón no está presente o no es clickeable
        return False

def get_xml_hash(file_path):
    """Genera un hash basado en el contenido XML para identificar duplicados."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extraer elementos clave que identifican un artículo único
        title_element = root.find(".//title")
        doi_element = root.find(".//doi")

        # Crear identificador con datos relevantes
        identifier = ""
        if title_element is not None and title_element.text:
            identifier += title_element.text.strip()
        if doi_element is not None and doi_element.text:
            identifier += doi_element.text.strip()

        # Si no hay datos específicos, usar todo el contenido
        if not identifier:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()

        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error al generar hash para {file_path}: {str(e)}")
        return hashlib.md5(file_path.encode('utf-8')).hexdigest()

def check_and_handle_duplicate(download_dir, xml_file_path):
    """Verifica si un archivo XML es duplicado."""
    # Rutas a los archivos de registro
    hash_registry_path = os.path.join(os.path.dirname(download_dir), "xml_hashes.json")
    repeated_json_path = os.path.join(os.path.dirname(download_dir), "repeated.json")

    # Cargar registros existentes o crear nuevos
    if os.path.exists(hash_registry_path):
        with open(hash_registry_path, 'r', encoding='utf-8') as f:
            hash_registry = json.load(f)
    else:
        hash_registry = []

    if os.path.exists(repeated_json_path):
        with open(repeated_json_path, 'r', encoding='utf-8') as f:
            repeated_records = json.load(f)
    else:
        repeated_records = []

    # Generar hash del archivo actual
    current_hash = get_xml_hash(xml_file_path)

    # Verificar si ya existe este hash
    is_duplicate = current_hash in hash_registry

    if is_duplicate:
        # Es un duplicado - añadir a repeated.json
        try:
            # Extraer información básica del XML
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            title_element = root.find(".//title")
            title = title_element.text if title_element is not None and title_element.text else "Sin título"

            # Crear entrada para repeated.json
            repeated_entry = {
                "filename": os.path.basename(xml_file_path),
                "title": title,
                "hash": current_hash,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            repeated_records.append(repeated_entry)

            # Guardar el registro actualizado
            with open(repeated_json_path, 'w', encoding='utf-8') as f:
                json.dump(repeated_records, f, ensure_ascii=False, indent=4)

            # Eliminar el archivo duplicado
            os.remove(xml_file_path)
            print(f"Duplicado detectado y registrado: {os.path.basename(xml_file_path)}")
        except Exception as e:
            print(f"Error al procesar duplicado {xml_file_path}: {str(e)}")
    else:
        # No es duplicado - añadir al registro de hashes
        hash_registry.append(current_hash)
        with open(hash_registry_path, 'w', encoding='utf-8') as f:
            json.dump(hash_registry, f)

    return is_duplicate

def search_and_download(driver, search_string, download_dir, max_files):
    """
    Realiza una búsqueda y descarga los archivos XML usando Selenium.
    """

    # 2) Esperar a que esté la caja de búsqueda, escribir la query y enviar
    caja = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.ID, "search-input"))
    )
    caja.clear()
    caja.send_keys(search_string, Keys.RETURN)

    # 3) Esperar a que carguen los resultados
    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.ID, "result-list"))
    )
    time.sleep(2)

    results_processed = 0
    successful_downloads = 0
    current_result_idx = 1

    while successful_downloads < max_files:
        try:
            print(f"Procesando resultado #{current_result_idx}…")
            btn_id = f"record-{current_result_idx}-tools-toggle-button"

            # Verificar si necesitamos cargar más resultados
            try:
                # Intentar encontrar el elemento actual
                tool_button = driver.find_element(By.ID, btn_id)
            except NoSuchElementException:
                # Si no encontramos el elemento, intentamos cargar más resultados
                print(f"No se encontró el resultado #{current_result_idx}, intentando cargar más resultados...")
                if not load_more_results(driver):
                    print("No hay más resultados para cargar o se alcanzó el límite. Finalizando.")
                    break

                # Verificar nuevamente si el elemento ya está disponible
                try:
                    tool_button = driver.find_element(By.ID, btn_id)
                except NoSuchElementException:
                    # Si aún no lo encontramos después de cargar más, podríamos haber llegado al final
                    print(
                        f"No se pudo encontrar el resultado #{current_result_idx} después de cargar más. Finalizando.")
                    break

            # Obtener el título del artículo para el nombre del archivo
            article_title = get_article_title(driver, current_result_idx)

            # 4) Abrir menú de herramientas
            button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.ID, btn_id))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)

            # 5) Seleccionar "Descargar"
            menu_xpath = f"//li[@id='record-{current_result_idx}-tools-item-3']"
            download_option = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, menu_xpath))
            )
            driver.execute_script("arguments[0].click();", download_option)
            time.sleep(0.5)  # Aumentamos el tiempo para que se muestre el diálogo

            # Asegurarse de estar en solo metadatos
            meta_option = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, "//li[text()='Solo metadatos']"))
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", meta_option)

            # 6) Seleccionar XML
            xml_radio = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, "//span[text()='XML']/ancestor::label"))
            )
            driver.execute_script("arguments[0].click();", xml_radio)
            time.sleep(1)

            # 7) Hacer clic en el botón de descarga
            download_button = WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable((By.XPATH, "//button[text()='Descargar']"))
            )
            driver.execute_script("arguments[0].click();", download_button)

            # 8) Esperar a que se complete la descarga
            if wait_for_download_complete(download_dir, timeout=20):
                # 9) Renombrar el archivo
                if rename_last_downloaded_file(download_dir, f"{current_result_idx}_{article_title}"):
                    successful_downloads += 1
            else:
                print(f"⚠ Tiempo de espera agotado para la descarga del resultado #{current_result_idx}")

            # 10) Cerrar el diálogo
            try:
                close_btn = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.XPATH, "//button[@title='Cerrar']"))
                )
                driver.execute_script("arguments[0].click();", close_btn)
            except:
                try:
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                except:
                    pass
            time.sleep(1)

            results_processed += 1
            print(
                f"✓ Resultado #{current_result_idx} procesado ({successful_downloads} descargados de {results_processed} procesados)\n")

            # Incrementar el índice para el siguiente resultado
            current_result_idx += 1

            # Si ya hemos alcanzado la cantidad máxima, terminar
            if successful_downloads >= max_files:
                break

        except TimeoutException:
            print(f"⚠ Timeout en resultado #{current_result_idx}, saltando.\n")
            current_result_idx += 1
            continue
        except Exception as e:
            print(f"❌ Error en resultado #{current_result_idx}: {str(e)}\n")
            # Intentar cerrar posibles modales sueltos
            try:
                driver.execute_script("document.body.click();")
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except Exception:
                pass
            current_result_idx += 1
            continue

    print(f"Proceso finalizado. Descargados {successful_downloads} de {results_processed} resultados procesados.")
    return successful_downloads


def main(search_string, mail, key, top_results):
    # Configuración
    browser_path = r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    download_dir = os.path.abspath("src/refs")
    os.makedirs(download_dir, exist_ok=True)

    print(f"Iniciando scraper para buscar '{search_string}' y descargar hasta {top_results} resultados")
    print(f"Los archivos XML se guardarán en: {download_dir}")

    driver = setup_driver(browser_path, download_dir)
    try:
        # Login
        log_into_library(driver, mail, key)
        # Búsqueda y descarga
        successful = search_and_download(driver, search_string, download_dir, top_results)
        print(f"Descarga completada. {successful} archivos descargados correctamente.")
    except Exception as e:
        print(f"Error general: {str(e)}")
    finally:
        print("Cerrando navegador...")
        driver.quit()


if __name__ == "__main__":
    # Eliminar credenciales hardcodeadas para seguridad
    email = input("Correo electrónico: ")
    password = input("Contraseña: ")
    query = input("Término de búsqueda: ")
    max_results = int(input("Número máximo de resultados a descargar: ") or "10")

    main(query, email, password, max_results)
