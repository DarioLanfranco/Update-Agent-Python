import os
import sys
import shutil

from core.validator import Validator
from core.updater import Updater
from core.downloader import Downloader
from core.notifier import Notifier
from lib.logger import Logger

# Ruta del archivo de configuración
CONFIG_PATH = "config/settings.json"

def main() -> None:
    """
    Orquesta el proceso de actualización del ERP:
    - Valida entorno
    - Detecta actualizaciones
    - Realiza backup de instalación actual
    - Descarga nueva versión (carpeta, exe, zip, etc)
    - Notifica resultados
    """
    logger = Logger().get_logger()
    notifier = Notifier()

    validator = Validator(CONFIG_PATH)
    if not validator.validate_all():
        logger.error("[Main] Falló la validación inicial. Abortando.")
        notifier.send_notification("ERP Update", "Falló la validación de configuración.")
        sys.exit(1)

    settings = validator.settings

    try:
        updater = Updater(settings.remote_version_url, settings.version_file)

        if not updater.is_update_available():
            logger.info("[Main] No hay actualizaciones disponibles.")
            notifier.send_notification("ERP Update", "No hay actualizaciones disponibles.")
            return

        new_version = updater.get_remote_version()
        logger.info(f"[Main] Nueva versión detectada: {new_version}")

        # Realizar respaldo de la carpeta de despliegue actual
        if os.path.exists(settings.backup_folder):
            shutil.rmtree(settings.backup_folder)
        shutil.copytree(settings.deploy_folder, settings.backup_folder)
        logger.info(f"[Main] Respaldo exitoso en: {settings.backup_folder}")

        # Descargar nuevo paquete
        downloader = Downloader(settings.download_url_template, settings.download_folder)
        package_path = downloader.download_package(new_version)

        if not package_path:
            logger.error("[Main] Descarga fallida. Abortando proceso.")
            notifier.send_notification("ERP Update", "Error al descargar el paquete de actualización.")
            sys.exit(1)

        logger.info(f"[Main] Paquete descargado en: {package_path}")
        notifier.send_notification("ERP Update", f"Actualización {new_version} descargada correctamente.")

    except Exception as e:
        logger.exception(f"[Main] Error inesperado durante la actualización: {e}")
        notifier.send_notification("ERP Update", "Fallo inesperado en la actualización.")
        sys.exit(1)


if __name__ == "__main__":
    main()
