"""
Actions para trámites generales (impugnación, reclamos, constancias)
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)

class ActionTramitesConstanciasNoAdeudo(Action):
    """Action para constancias de no adeudo"""

    def name(self) -> Text:
        return "action_tramites_constancias_no_adeudo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de constancias de no adeudo")

        message = """📋 **CONSTANCIAS DE NO ADEUDO**

Puede obtener su constancia de no adeudo por deuda tributaria:

🔗 **Agencia Virtual SAT:**
📌 https://www.sat.gob.pe/ciudadano

**Pasos:**
1. Acceda con su usuario y contraseña
2. Ubique el módulo de "Constancia de no Adeudo Tributaria"

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []