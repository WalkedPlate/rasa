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
3. Buscar la opción "Cuadernillo Tributario"
4. Descargar o consultar online

📖 **Guía paso a paso:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Qué más necesitas?**
• 'Cuadernillo por código' - Acceso con código de contribuyente
• 'Consultar deuda' - Ver cuánto debes
• 'Menú principal' - Otras opciones

💡 **Tip:** El cuadernillo contiene todo el historial de tus impuestos prediales y vehiculares."""

        dispatcher.utter_message(text=message)
        return []


class ActionCuadernilloPredial(Action):
    """Action para cuadernillo predial por código de contribuyente"""

    def name(self) -> Text:
        return "action_cuadernillo_predial"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de cuadernillo predial")

        message = """🏠 **CUADERNILLO PREDIAL**

Para acceder a tu cuadernillo predial:

🔗 **Acceso directo:**
https://www.sat.gob.pe/websitev9/TributosMultas/PredialyArbitrios/CuadernilloTributario

**¿Qué necesitas?**
• Tu **código de contribuyente**
• La **contraseña** de tu cuadernillo predial (de cualquier año)

**Pasos:**
1. Hacer clic en "Ver mi cuadernillo"
2. Ingresar código de contribuyente
3. Ingresar contraseña del cuadernillo
4. Consultar información

**¿Qué más necesitas?**
• 'Consultar deuda predial' - Ver cuánto debes
• 'Cuadernillo vehicular' - Para impuesto vehicular
• 'Agencia Virtual' - Acceso completo online
• 'Menú principal' - Otras opciones

💡 **Tip:** Si no recuerdas tu código de contribuyente, búscalo en cualquier recibo de impuesto predial anterior."""

        dispatcher.utter_message(text=message)
        return []


class ActionCuadernilloVehicular(Action):
    """Action para cuadernillo vehicular por código de contribuyente"""

    def name(self) -> Text:
        return "action_cuadernillo_vehicular"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de cuadernillo vehicular")

        message = """🚗 **CUADERNILLO VEHICULAR**

Para acceder a tu cuadernillo vehicular:

🔗 **Acceso directo:**
https://www.sat.gob.pe/websitev9/TributosMultas/ImpuestoVehicular/CuadernilloTributario

**¿Qué necesitas?**
• Tu **código de contribuyente**
• La **contraseña** de tu cuadernillo vehicular (de cualquier año)

**Pasos:**
1. Hacer clic en "Ver mi cuadernillo"
2. Ingresar código de contribuyente
3. Ingresar contraseña del cuadernillo
4. Consultar información

**¿Qué más necesitas?**  
• 'Consultar deuda vehicular' - Ver cuánto debes
• 'Cuadernillo predial' - Para impuesto predial
• 'Agencia Virtual' - Acceso completo online
• 'Menú principal' - Otras opciones

💡 **Tip:** El código de contribuyente también aparece en tu SOAT o en recibos anteriores del impuesto vehicular."""

        dispatcher.utter_message(text=message)
        return []