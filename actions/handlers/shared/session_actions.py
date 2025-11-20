"""
Actions relacionados con el manejo de sesión
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
import logging
import random
from datetime import datetime

from actions.api.backend_client import backend_client

logger = logging.getLogger(__name__)


class ActionFinalizarChat(Action):
    """Finaliza la conversación con mensaje dinámico"""

    def name(self) -> Text:
        return "action_finalizar_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender_id = tracker.sender_id

        # Llamar endpoint de cierre antes del mensaje
        self._close_assistance_if_exists(sender_id)

        # Obtener mensaje de despedida dinámico del backend
        mensaje = self._get_farewell_message()

        dispatcher.utter_message(text=mensaje)

        # Log para el sistema
        logger.info(f"Conversación finalizada para usuario: {sender_id} - {datetime.now()}")

        return [Restarted()]

    def _get_farewell_message(self) -> str:
        """
        Obtiene mensaje de despedida dinámico desde el backend CRM

        Returns:
            str: Mensaje de despedida personalizado o mensaje por defecto si falla
        """
        try:
            # Intentar obtener mensajes del backend
            farewell_messages = backend_client.get_farewell_messages()

            if farewell_messages and len(farewell_messages) > 0:
                # Si hay múltiples mensajes, seleccionar uno aleatorio
                mensaje_despedida = random.choice(farewell_messages)
                logger.info(f"Mensaje de despedida obtenido del backend: '{mensaje_despedida}'")

                # Agregar información adicional del SAT
                mensaje_completo = f"""{mensaje_despedida}

📞 **¿Necesitas más ayuda?** Escribe 'hola' cuando regreses
🌐 **Web del SAT:** www.sat.gob.pe"""

                return mensaje_completo
            else:
                logger.warning("No se obtuvieron mensajes de despedida del backend, usando mensaje por defecto")
                return self._get_default_farewell_message()

        except Exception as e:
            logger.error(f"Error obteniendo mensaje de despedida del backend: {e}")
            return self._get_default_farewell_message()

    def _get_default_farewell_message(self) -> str:
        """
        Mensaje de despedida por defecto si falla la consulta al backend

        Returns:
            str: Mensaje de despedida estático
        """
        return """¡Gracias por usar el chatbot del SAT de Lima! 👋

¡Que tengas un excelente día! 😊"""

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