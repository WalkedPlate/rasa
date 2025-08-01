"""
Actions relacionados con el manejo de sesión
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionFinalizarChat(Action):
    """Finaliza la conversación de manera elegante"""

    def name(self) -> Text:
        return "action_finalizar_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = tracker.sender_id

        # Mensaje personalizado de despedida
        mensaje = """¡Gracias por usar el SAT de Lima! 👋

Tu conversación ha sido guardada exitosamente.

📞 **¿Necesitas más ayuda?** Escribe 'hola' cuando regreses
🌐 **Web del SAT:** www.sat.gob.pe
📱 **Mesa de partes digital:** Para trámites online

¡Que tengas un excelente día! 😊"""

        dispatcher.utter_message(text=mensaje)

        # Log para el sistema
        logger.info(f" Conversación finalizada para usuario: {sender_id} - {datetime.now()}")

        return [Restarted()]