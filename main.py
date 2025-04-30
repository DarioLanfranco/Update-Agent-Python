# main.py

import os
import sys
import shutil

from core.validator import Validator
from core.updater import Updater
from core.downloader import Downloader
from core.installer import Installer
from core.notifier import Notifier
from lib.logger import Logger

# Ruta del archivo de configuración
CONFIG_PATH = "config/settings.json"

# Carpeta del ERP en uso (instalación activa)
SOURCE_FOLDER = "C:\\Oliver\\Sinergial"

# Carpeta donde se guardará el backup completo de Sinergial
BACKUP_FOLDER = "C:\\Oliver\\Backup\\copia-Sinergial"


def backup_sinergial(logger) -> bool:
    """
    Realiza una copia de seguridad de C:\Oliver\Sinergial hacia C:\Oliver\Backup\copia-Sinergial
    """
    try:
        if not os.path.exists(SOURCE_FOLDER):
            logger.error(f"[Backup] Carpeta de origen no encontrada: {SOURCE_FOLDER}")
            return False

        if os.path.exists(BACKUP_FOLDER):
            logger.info(f"[Backup] Eliminando backup anterior: {BACKUP_FOLDER}")
            shutil.rmtree(BACKUP_FOLDER)

        shutil.copytree(SOURCE_FOLDER, BACKUP_FOLDER)
        logger.info(f"[Backup] Backup exitoso de Sinergial en: {BACKUP_FOLDER}")
        return True

    except Exception as e:
        logger.exception(f"[Backup] Error durante backup de Sinergial: {e}")
        return False


def main() -> None:
    """
    Orquesta el proceso de actualización:
    - Valida configuración
    - Verifica nuevas versiones
    - Descarga el paquete si es necesario
    - Realiza backup de instalación en uso (Sinergial)
    - Descomprime en carpeta temporal (deploy_folder)
    - Actualiza archivo de versión
    - Notifica resultado
    """
    logger = Logger().get_logger()
    notifier = Notifier()

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

        new_version = updater.get_remote_version()
        logger.info(f"[Main] Nueva versión detectada: {new_version}")

        downloader = Downloader(settings.download_url_template, settings.download_folder)
        package_path = downloader.download_package(new_version)

        if not package_path:
            logger.error("[Main] Descarga fallida. Abortando proceso.")
            notifier.send_notification("ERP Update", "Error al descargar el paquete de actualización.")
            sys.exit(1)

        # Backup de Sinergial antes de hacer cualquier instalación
        if not backup_sinergial(logger):
            logger.error("[Main] Falló el backup de Sinergial. Abortando.")
            notifier.send_notification("ERP Update", "Error al hacer backup de Sinergial.")
            sys.exit(1)

        installer = Installer(settings.deploy_folder, settings.version_file)

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
