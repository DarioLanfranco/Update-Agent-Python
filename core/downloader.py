# core/downloader.py

import os
import requests


class Downloader:
    """
    Clase encargada de descargar el paquete de actualización del ERP
    desde un servidor remoto utilizando HTTP.
    """

    def __init__(self, download_url_template: str, download_folder: str):
        """
        Inicializa el Downloader con:
        - download_url_template: plantilla de URL donde descargar, e.g., "https://servidor/erp_{version}.zip"
        - download_folder: carpeta local donde guardar el paquete descargado
        """
        self.download_url_template = download_url_template
        self.download_folder = download_folder

    def download_package(self, version: str) -> str:
        """
        Descarga el paquete de actualización correspondiente a una versión específica.
        Retorna la ruta local del archivo descargado o una cadena vacía si falla.
        """
        try:
            # Construir URL final reemplazando {0} por el número de versión
            download_url = self.download_url_template.format(version)

            # Extraer el nombre de archivo de la URL
            filename = download_url.split("/")[-1]

            # Construir la ruta de destino completa
            destination = os.path.join(self.download_folder, filename)

            print(f"[Downloader] Descargando desde: {download_url}")
            print(f"[Downloader] Guardando en: {destination}")

            # Verificar que la carpeta de descarga exista
            os.makedirs(self.download_folder, exist_ok=True)

            # Iniciar descarga segura con requests
            with requests.get(download_url, stream=True, timeout=30) as response:
                response.raise_for_status()  # Lanzar excepción si respuesta HTTP no es 2xx

                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            print("[Downloader] Descarga completada exitosamente.")
            return destination

        except requests.HTTPError as e:
            print(f"[Downloader] Error HTTP durante descarga: {e}")
            return ""
        except requests.ConnectionError as e:
            print(f"[Downloader] Error de conexión al servidor: {e}")
            return ""
        except requests.Timeout as e:
            print(f"[Downloader] Tiempo de espera agotado durante descarga: {e}")
            return ""
        except Exception as e:
            print(f"[Downloader] Error inesperado durante descarga: {e}")
            return ""


if __name__ == "__main__":
    # Simulación manual de descarga para pruebas locales
    import json

    try:
        with open("config/settings.json", 'r', encoding='utf-8') as f:
            settings = json.load(f)

        download_url_template = settings["download_url_template"]
        download_folder = settings["download_folder"]

        downloader = Downloader(download_url_template, download_folder)

        # Simular descarga de versión "1.2.3"
        version = "1.2.3"
        package_path = downloader.download_package(version)

        if package_path:
            print(f"[Downloader] Paquete descargado exitosamente en: {package_path}")
        else:
            print("[Downloader] Fallo en la descarga del paquete.")

    except Exception as e:
        print(f"[Downloader] Error cargando configuración de prueba: {e}")
