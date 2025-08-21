"""
Actions para trámites generales (impugnación, reclamos, constancias)
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionTramitesImpugnacionPapeletas(Action):
    """Action para impugnación de papeletas"""

    def name(self) -> Text:
        return "action_tramites_impugnacion_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de impugnación de papeletas")

        message = """📋 **IMPUGNACIÓN DE PAPELETAS**

Para requisitos detallados de impugnación de papeletas:

🔗 **Requisitos completos:**
📌 https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA

📋 **Descargue y consulte el llenado del formato:**
📌 https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Requisitos papeletas' - Ver otros trámites de papeletas
• 'Consultar trámite' - Estado de tu trámite
• 'Otros trámites' - Volver al menú de trámites
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesReclamoTributario(Action):
    """Action para reclamo tributario"""

    def name(self) -> Text:
        return "action_tramites_reclamo_tributario"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de reclamo tributario")

        message = """📋 **RECLAMO TRIBUTARIO**

Para reclamaciones tributarias:

🔗 **Requisitos completos:**
📌 https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA

📋 **Descargue y consulte el llenado del formato:**
📌 https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Requisitos tributarios' - Ver otros trámites tributarios
• 'Consultar trámite' - Estado de tu trámite
• 'Otros trámites' - Volver al menú de trámites
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


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
3. Descargue su constancia

**¿Qué más necesitas?**
• 'Agencia Virtual' - Información sobre registro
• 'Consultar deuda' - Ver si tienes deuda pendiente
• 'Otros trámites' - Volver al menú de trámites
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []