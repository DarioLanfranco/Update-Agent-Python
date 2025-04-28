# core/installer.py

import os
import shutil
import zipfile


class Installer:
    """
    Clase encargada de aplicar el paquete de actualización del ERP:
    - Realiza un respaldo (backup) de la versión actual.
    - Instala la nueva versión extraída desde un archivo comprimido.
    - Actualiza el archivo de versión local.
    - Protege la carpeta 'Data' para preservar la base de datos del cliente.
    """

    def __init__(self, deploy_folder: str, version_file: str):
        """
        Inicializa el instalador con:
        - deploy_folder: carpeta donde se encuentra el ERP instalado.
        - version_file: archivo donde se guarda la versión instalada.
        """
        self.deploy_folder = deploy_folder
        self.version_file = version_file

    def backup_current_version(self, backup_folder: str) -> bool:
        """
        Realiza una copia de respaldo de la instalación actual.
        Elimina cualquier backup previo existente.
        Retorna True si el backup fue exitoso, False en caso de error.
        """
        try:
            if not os.path.exists(self.deploy_folder):
                print(f"[Installer] Carpeta de despliegue no encontrada: {self.deploy_folder}")
                return False

            if os.path.exists(backup_folder):
                print(f"[Installer] Eliminando respaldo anterior: {backup_folder}")
                shutil.rmtree(backup_folder)

            shutil.copytree(self.deploy_folder, backup_folder)
            print(f"[Installer] Respaldo realizado exitosamente en: {backup_folder}")
            return True

        except Exception as e:
            print(f"[Installer] Error durante el respaldo: {e}")
            return False

    def install_update(self, package_path: str, new_version: str) -> bool:
        """
        Aplica el paquete de actualización descargado:
        - Extrae el contenido del ZIP evitando sobrescribir la carpeta 'Data'.
        - Actualiza el archivo de versión local.
        Retorna True si todo fue exitoso, False en caso de error.
        """
        try:
            if not os.path.isfile(package_path):
                print(f"[Installer] Paquete de actualización no encontrado: {package_path}")
                return False

            print(f"[Installer] Iniciando extracción del paquete en: {self.deploy_folder}")

            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # Ignorar cualquier archivo o carpeta dentro de 'Data/'
                    if member.startswith("Data/") or member.startswith("Data\\"):
                        print(f"[Installer] Ignorando carpeta protegida durante actualización: {member}")
                        continue
                    zip_ref.extract(member, self.deploy_folder)

            # Actualizar archivo de versión
            os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(new_version)

            print(f"[Installer] Versión actualizada correctamente a: {new_version}")
            return True

        except zipfile.BadZipFile:
            print(f"[Installer] Error: el archivo ZIP está corrupto o no es válido.")
            return False
        except Exception as e:
            print(f"[Installer] Error inesperado durante la instalación: {e}")
            return False


if __name__ == "__main__":
    # Prueba manual del instalador
    import json

    try:
        # Cargar configuración desde settings.json
        with open("config/settings.json", 'r', encoding='utf-8') as f:
            settings = json.load(f)

        deploy_folder = settings["deploy_folder"]
        version_file = settings["version_file"]

        installer = Installer(deploy_folder, version_file)

        # Definir carpeta donde se hará el respaldo
        backup_folder = "C:\\ERP\\Backup"

        # Simular flujo de instalación de prueba
        if installer.backup_current_version(backup_folder):
            if installer.install_update("path/to/package.zip", "1.2.3"):
                print("[Installer] Actualización aplicada exitosamente.")
            else:
                print("[Installer] Fallo aplicando actualización.")
        else:
            print("[Installer] Fallo realizando respaldo.")

    except Exception as e:
        print(f"[Installer] Error durante la prueba del instalador: {e}")
    except json.JSONDecodeError as e:
        print(f"[Installer] Error al cargar configuración JSON: {e}")