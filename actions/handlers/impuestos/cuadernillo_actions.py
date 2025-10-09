"""
Actions para cuadernillo tributario
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionCuadernilloAgenciaVirtual(Action):
    """Action para cuadernillo tributario vía Agencia Virtual"""

    def name(self) -> Text:
        return "action_cuadernillo_agencia_virtual"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de cuadernillo vía Agencia Virtual")

        message = """📋 **CUADERNILLO TRIBUTARIO - AGENCIA VIRTUAL**

Para acceder a tu cuadernillo tributario:

🔗 **Regístrate en Agencia Virtual SAT:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**Pasos:**
1. Crear tu usuario y contraseña
2. Ingresar con tus datos
3. Buscar Otras consultas / opción "Cuadernillo Tributario"

📖 **Guía paso a paso:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
   """

        dispatcher.utter_message(text=message)
        return []
