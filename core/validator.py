# core/validator.py

import os
import json
import socket
from typing import Optional
from pydantic import BaseModel, ValidationError


class Settings(BaseModel):
    """
    Modelo de datos para la configuración cargada desde settings.json.
    Utiliza pydantic para validación automática.
    """
    version_file: str
    remote_version_url: str
    download_url_template: str
    download_folder: str
    deploy_folder: str
    notify_type: str


class Validator:
    """
    Clase encargada de validar que la configuración y el entorno sean correctos
    antes de ejecutar cualquier operación en el sistema.
    """

    def __init__(self, config_path: str):
        """
        Inicializa el validador con la ruta al archivo de configuración.
        """
        self.config_path = config_path
        self.settings: Optional[Settings] = None
        print(f"[Validator] Inicializando con configuración en: {self.config_path}")

    def load_settings(self) -> bool:
        """
        Carga y valida el archivo settings.json.
        Retorna True si fue exitoso, False si hubo errores.
        """
        try:
            if not os.path.isfile(self.config_path):
                print(f"[Validator] Archivo de configuración no encontrado: {self.config_path}")
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.settings = Settings(**data)
            print("[Validator] Configuración cargada correctamente.")
            return True

        except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
            print(f"[Validator] Error cargando o validando configuración: {e}")
            return False
        except Exception as e:
            print(f"[Validator] Error inesperado al cargar configuración: {e}")
            return False

    def check_folders(self) -> bool:
        """
        Verifica la existencia de las carpetas necesarias (descarga y despliegue).
        Crea las carpetas si no existen.
        """
        try:
            if not self.settings:
                raise ValueError("Configuración no cargada.")

            folders = [
                self.settings.download_folder,
                self.settings.deploy_folder
            ]

            for folder in folders:
                if not os.path.exists(folder):
                    print(f"[Validator] Carpeta no encontrada, creando: {folder}")
                    os.makedirs(folder, exist_ok=True)

            print("[Validator] Carpetas verificadas/correctas.")
            return True

        except Exception as e:
            print(f"[Validator] Error verificando o creando carpetas: {e}")
            return False

    def check_server_connectivity(self) -> bool:
        """
        Verifica que haya conectividad al servidor de actualizaciones (resuelve DNS).
        """
        try:
            if not self.settings:
                raise ValueError("Configuración no cargada.")

            # Extraer el hostname del URL remoto
            host = self.settings.remote_version_url.replace('https://', '').replace('http://', '').split('/')[0]
            socket.gethostbyname(host)
            print(f"[Validator] Conexión exitosa a {host}")
            return True

        except socket.gaierror:
            print(f"[Validator] Error: No se puede resolver el nombre del servidor.")
            return False
        except Exception as e:
            print(f"[Validator] Error verificando conectividad: {e}")
            return False

    def validate_all(self) -> bool:
        """
        Ejecuta la validación completa del sistema:
        - Cargar configuración
        - Verificar carpetas necesarias
        - Verificar conectividad con servidor
        """
        print("[Validator] Iniciando validación completa...")

        if not self.load_settings():
            return False

        if not self.check_folders():
            return False

        if not self.check_server_connectivity():
            return False

        print("[Validator] Validación completa exitosa.")
        return True


if __name__ == "__main__":
    # Ejecución manual de pruebas del validador
    validator = Validator("config/settings.json")
    if validator.validate_all():
        print("[Validator] Todo OK.")
    else:
        print("[Validator] Fallo en validación.")
