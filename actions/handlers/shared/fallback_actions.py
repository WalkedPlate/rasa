"""
Actions para manejo inteligente de fallback
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

logger = logging.getLogger(__name__)


class ActionSmartFallback(Action):
    """Fallback progresivo: nivel 1 sin asesor, nivel 2+ con asesor"""

    def name(self) -> Text:
        return "action_smart_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fallback_count = tracker.get_slot("fallback_count") or 0
        fallback_count += 1

        logger.info(f"Fallback #{fallback_count} para usuario {tracker.sender_id}")

        # Solo 2 mensajes diferentes
        if fallback_count == 1:
            message = """No entendí completamente tu mensaje. Déjame ayudarte 😊

📋 **OPCIONES PRINCIPALES:**
Escribe el nombre de la opción que necesitas:
🔹 **Casilla MTC** - "Casilla MTC" o "Registro"
🔹 **Pagos** - "Pagos" o "Cómo pago"  
🔹 **Papeletas** - "Papeletas" o "Multas"
🔹 **Impuestos** - "Impuestos" o "Deuda tributaria"
🔹 **Retención** - "Retención" o "Orden de captura"
🔹 **Actualizar datos** - "Actualizar datos"
🔹 **Lugares y pagos** - "Oficinas" o "Lugares de pago"
🔹 **Servicios virtuales** - "Servicios virtuales"
🔹 **Trámites** - "Trámites"

💡 **También puedes decir:** "Menú principal"

¿En qué puedo ayudarte?"""

        else:  # 2 o más
            message = """Veo que aún no encuentro lo que buscas 🤔

📋 **Intenta escribir:**
- "Papeletas" - Para consultar multas
- "Impuestos" - Para deuda tributaria
- "Pagos" - Para información de pagos
- "Menú principal" - Ver todas las opciones

👨‍💼 **¿Necesitas ayuda personalizada?**
Escribe **"solicitar asesor"** para hablar con un asesor.
"""

        dispatcher.utter_message(text=message)
        return [SlotSet("fallback_count", fallback_count)]


class ActionResetFallbackCount(Action):
    """Resetea el contador cuando hay interacción exitosa"""

    def name(self) -> Text:
        return "action_reset_fallback_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_count = tracker.get_slot("fallback_count") or 0

        if current_count > 0:
            logger.info(f"Reseteando contador fallback para {tracker.sender_id} (era {current_count})")

        return [SlotSet("fallback_count", 0)]