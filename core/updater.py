# core/updater.py

import os
import requests


class Updater:
    """
    Clase encargada de manejar la detección de actualizaciones de la aplicación ERP.
    Se conecta a un servidor remoto para comparar versiones y determinar si hay una nueva disponible.
    """

    def __init__(self, remote_version_url: str, version_file: str):
        """
        Inicializa el Updater con la URL remota de versión y el archivo local de versión.
        """
        self.remote_version_url = remote_version_url
        self.version_file = version_file

    def get_local_version(self) -> str:
        """
        Obtiene la versión actualmente instalada desde el archivo local.
        Retorna '0.0.0' si el archivo no existe o no puede leerse.
        """
        try:
            if not os.path.isfile(self.version_file):
                print(f"[Updater] Archivo de versión local no encontrado: {self.version_file}")
                return "0.0.0"

            with open(self.version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                print(f"[Updater] Versión local detectada: {version}")
                return version

        except Exception as e:
            print(f"[Updater] Error leyendo versión local: {e}")
            return "0.0.0"

    def get_remote_version(self) -> str:
        """
        Obtiene la versión más reciente disponible desde el servidor remoto.
        Retorna '0.0.0' si hay errores de conexión o de formato.
        """
        try:
            response = requests.get(self.remote_version_url, timeout=10)
            response.raise_for_status()
            version = response.text.strip()
            print(f"[Updater] Versión remota detectada: {version}")
            return version

        except requests.RequestException as e:
            print(f"[Updater] Error de conexión al servidor de actualizaciones: {e}")
            return "0.0.0"
        except Exception as e:
            print(f"[Updater] Error inesperado obteniendo versión remota: {e}")
            return "0.0.0"

    def is_update_available(self) -> bool:
        """
        Compara la versión local y la remota.
        Retorna True si la versión remota es mayor (hay actualización disponible).
        """
        local_version = self.get_local_version()
        remote_version = self.get_remote_version()

        if remote_version == "0.0.0":
            print("[Updater] No se pudo determinar la versión remota, abortando comparación.")
            return False

        if remote_version > local_version:
            print("[Updater] ¡Nueva actualización disponible!")
            return True
        else:
            print("[Updater] No hay actualizaciones disponibles.")
            return False


if __name__ == "__main__":
    # Carga manual de configuración para pruebas locales
    import json

    try:
        with open("config/settings.json", 'r', encoding='utf-8') as f:
            settings = json.load(f)

        remote_version_url = settings["remote_version_url"]
        version_file = settings["version_file"]

        updater = Updater(remote_version_url, version_file)

        if updater.is_update_available():
            print("[Updater] Nueva actualización disponible.")
        else:
            print("[Updater] No hay actualizaciones disponibles.")

    except Exception as e:
        print(f"[Updater] Error al cargar configuración: {e}")
