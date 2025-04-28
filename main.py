# main.py

import os
import sys

from core.validator import Validator
from core.updater import Updater
from core.downloader import Downloader
from core.installer import Installer
from core.notifier import Notifier
from lib.logger import Logger

# Ruta del archivo de configuración
CONFIG_PATH = "config/settings.json"

# Ruta fija donde guardar los respaldos
BACKUP_FOLDER = "C:\\ERP\\Backup"


def main() -> None:
    """
    Función principal que orquesta todo el proceso de actualización del ERP.
    - Valida entorno
    - Detecta actualizaciones
    - Descarga nueva versión
    - Realiza backup de instalación actual
    - Instala la nueva versión
    - Notifica resultados
    """
    logger = Logger().get_logger()
    notifier = Notifier()

    # Validar configuración inicial
    validator = Validator(CONFIG_PATH)

    if not validator.validate_all():
        logger.error("[Main] Falló la validación inicial. Abortando proceso.")
        notifier.send_notification("ERP Update", "Falló la validación de configuración.")
        sys.exit(1)

    settings = validator.settings

    try:
        updater = Updater(settings.remote_version_url, settings.version_file)

        if not updater.is_update_available():
            logger.info("[Main] No hay actualizaciones disponibles.")
            notifier.send_notification("ERP Update", "No hay actualizaciones disponibles.")
            return

        # Obtener versión nueva
        new_version = updater.get_remote_version()
        logger.info(f"[Main] Nueva versión detectada: {new_version}")

        downloader = Downloader(settings.download_url_template, settings.download_folder)
        package_path = downloader.download_package(new_version)

        if not package_path:
            logger.error("[Main] Descarga fallida. Abortando proceso.")
            notifier.send_notification("ERP Update", "Error al descargar el paquete de actualización.")
            sys.exit(1)

        installer = Installer(settings.deploy_folder, settings.version_file)

        # Realizar respaldo de la instalación actual
        if not installer.backup_current_version(BACKUP_FOLDER):
            logger.error("[Main] Falló el respaldo. Abortando proceso.")
            notifier.send_notification("ERP Update", "Error al realizar respaldo de ERP.")
            sys.exit(1)

        # Aplicar la nueva actualización
        if not installer.install_update(package_path, new_version):
            logger.error("[Main] Falló la instalación de actualización.")
            notifier.send_notification("ERP Update", "Error instalando nueva actualización.")
            sys.exit(1)

        logger.info(f"[Main] Actualización a versión {new_version} completada exitosamente.")
        notifier.send_notification("ERP Update", f"Actualización a versión {new_version} completada.")

    except Exception as e:
        logger.exception(f"[Main] Error inesperado durante el proceso de actualización: {e}")
        notifier.send_notification("ERP Update", "Fallo inesperado en la actualización.")
        sys.exit(1)


if __name__ == "__main__":
    main()
    # Ejecutar la función principal