"""
Actions relacionados con solicitud de asesor humano
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

from actions.api.backend_client import backend_client

logger = logging.getLogger(__name__)


class ActionSolicitarAsesor(Action):
    """Solicita un asesor humano para atender al ciudadano"""

    def name(self) -> Text:
        return "action_solicitar_asesor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        phone_number = tracker.sender_id

        logger.info(f"Usuario {phone_number} solicita asesor humano")

        try:
            # Llamar al endpoint para solicitar asesor
            success, message = backend_client.request_advisor(phone_number)

            if success:
                # Éxito: El bot debe dejar de responder después de este mensaje
                response_message = self._format_success_message()
                dispatcher.utter_message(text=response_message)

                logger.info(f"Asesor solicitado exitosamente para {phone_number}")

                # Marcar que se solicitó asesor (para logs/métricas)
                return [SlotSet("asesor_solicitado", True)]

            else:
                # Error: Mostrar mensaje de disculpa y alternativas
                response_message = self._format_error_message(message)
                dispatcher.utter_message(text=response_message)

                logger.warning(f"No se pudo solicitar asesor para {phone_number}: {message}")
                return []

        except Exception as e:
            logger.error(f"Error inesperado solicitando asesor para {phone_number}: {e}")

            error_message = self._format_unexpected_error_message()
            dispatcher.utter_message(text=error_message)
            return []

    def _format_success_message(self) -> str:
        """Mensaje cuando la solicitud es exitosa"""
        return """**¡Solicitud enviada exitosamente!**

👨‍💼 **Un asesor te atenderá pronto**

📱 **Mantén esta conversación abierta**

"""

    def _format_error_message(self, error_msg: str) -> str:
        """Mensaje cuando hay error específico"""
        return f"""❌ **Por el momento no contamos con esta opción**

**🌐 Puedes consultar en:**
- www.sat.gob.pe
- Escribir 'menú principal' para continuar explorando otras opciones

¿Hay algo más en lo que pueda ayudarte?"""

    def _format_unexpected_error_message(self) -> str:
        """Mensaje cuando hay error inesperado"""
        return """😔 **Error temporal del sistema**

No pudimos procesar tu solicitud en este momento.

**🌐 Te recomendamos:**
- Consultar en: www.sat.gob.pe

**🔄 O intenta nuevamente en unos minutos:**

¿Qué más necesitas?"""