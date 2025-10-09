# actions/shared/session_actions.py
"""
Actions relacionados con el manejo de sesión
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
import logging
from datetime import datetime

from actions.api.backend_client import backend_client

logger = logging.getLogger(__name__)


class ActionFinalizarChat(Action):
    """Finaliza la conversación de manera elegante"""

    def name(self) -> Text:
        return "action_finalizar_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id

        # Llamar endpoint de cierre antes del mensaje
        self._close_assistance_if_exists(sender_id)

        # Mensaje de despedida consistente con el estilo del proyecto
        mensaje = """¡Gracias por usar el chatbot del SAT de Lima! 👋

📞 **¿Necesitas más ayuda?** Escribe 'hola' cuando regreses
🌐 **Web del SAT:** www.sat.gob.pe

¡Que tengas un excelente día! 😊"""

        dispatcher.utter_message(text=mensaje)

        # Log para el sistema
        logger.info(f"Conversación finalizada para usuario: {sender_id} - {datetime.now()}")

        return [Restarted()]

    def _close_assistance_if_exists(self, phone_number: str) -> None:
        """
        Intenta cerrar la asistencia activa para el usuario

        Args:
            phone_number: Número de teléfono del usuario
        """
        try:
            logger.info(f"Intentando cerrar asistencia para: {phone_number}")

            # Llamar al endpoint de cierre
            success, message = backend_client.close_assistance(phone_number)

            if success:
                logger.info(f"Asistencia cerrada exitosamente para {phone_number}: {message}")
            else:
                logger.warning(f"No se pudo cerrar asistencia para {phone_number}: {message}")

        except Exception as e:
            # No fallar el flujo principal si hay error cerrando asistencia
            logger.error(f"Error inesperado cerrando asistencia para {phone_number}: {e}")

