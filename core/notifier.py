# core/notifier.py

from plyer import notification


class Notifier:
    """
    Clase encargada de enviar notificaciones visuales al usuario.
    Utiliza la librería 'plyer' para generar popups compatibles con Windows, Linux y macOS.
    """

    def __init__(self, app_name: str = "ERP Update Agent"):
        """
        Inicializa el notificador.
        - app_name: Nombre que aparecerá como remitente de la notificación.
        """
        self.app_name = app_name

    def send_notification(self, title: str, message: str, timeout: int = 10) -> bool:
        """
        Envía una notificación de escritorio al usuario.
        - title: Título de la notificación.
        - message: Mensaje descriptivo de la notificación.
        - timeout: Tiempo (en segundos) que permanecerá visible (default: 10).
        Retorna True si la notificación fue enviada, False en caso de error.
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout
            )
            print(f"[Notifier] Notificación enviada: {title}")
            return True

        except Exception as e:
            print(f"[Notifier] Error enviando notificación: {e}")
            return False


if __name__ == "__main__":
    # Prueba manual del sistema de notificaciones
    try:
        notifier = Notifier()
        if notifier.send_notification(
            title="Actualización Exitosa",
            message="La actualización del ERP se ha completado correctamente."
        ):
            print("[Notifier] Prueba de notificación exitosa.")
        else:
            print("[Notifier] Fallo en la prueba de notificación.")

    except Exception as e:
        print(f"[Notifier] Error durante la prueba de notificación: {e}")
