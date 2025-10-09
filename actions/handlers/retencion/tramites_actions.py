"""
Actions para trámites de retención y captura (respuestas simples)
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionRetencionEmbargo(Action):
    """Action para información sobre retención o embargo de cuentas"""

    def name(self) -> Text:
        return "action_retencion_embargo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de retención o embargo de cuentas")

        message = """🏦 **RETENCIÓN O EMBARGO DE CUENTAS**

Si tiene retención bancaria debe realizar el pago de la deuda y comunicarse vía correo:

📧 **Correo:** asuservicio@sat.gob.pe:

• Nombres y apellidos completos
• Número de DNI

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionRetencionVehiculoInternado(Action):
    """Action para consulta de vehículo internado"""

    def name(self) -> Text:
        return "action_retencion_vehiculo_internado"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de vehículo internado")

        message = """🚗 **CONSULTAR VEHÍCULO INTERNADO**

Para consultar si su vehículo se encuentra internado:

🔗 **Consulta online:**
https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=7

• Opción "Internamiento de vehículo"
• Ingresa los datos solicitados

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionRetencionSuspenderCobranza(Action):
    """Action para solicitud de suspensión de cobranza coactiva"""

    def name(self) -> Text:
        return "action_retencion_suspender_cobranza"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de suspensión de cobranza coactiva")

        message = """📝 **SOLICITUD DE SUSPENSIÓN DE COBRANZA COACTIVA**

**Requisitos necesarios:**

1. **Formato de solicitud** debidamente llenado y firmado
   • En casos de deuda no tributaria: un formato por cada deuda

2. **Domicilio** real o procesal dentro del radio urbano de la provincia de Lima

3. **En caso de representación:** poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT

4. **Marcar la causal** según el formato y adjuntar los sustentos correspondientes

📋 **Documentos y enlaces:**

🔗 **Directiva:**
https://www.sat.gob.pe/WebSiteV8/Modulos/documentos/TUPA/Directiva_001-006-000000023_aprobada_por_RJ_001-004-00003951.pdf

🔗 **Formato:**
https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

🔗 **Mesa de Partes Digital:**
https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionRetencionTerceriaPropiedad(Action):
    """Action para tercería de propiedad"""

    def name(self) -> Text:
        return "action_retencion_terceria_propiedad"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de tercería de propiedad")

        message = """⚖️ **TERCERÍA DE PROPIEDAD**

🔗 **Requisitos:**
https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA

🔗 **Formato:**
https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

🔗 **Presentación del trámite:**
Mesa de Partes Digital: https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []

class ActionRetencionRemateVehicular(Action):
    """Action para información sobre remate vehicular"""

    def name(self) -> Text:
        return "action_retencion_remate_vehicular"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de remate vehicular")

        message = """🔨 **REMATE VEHICULAR**

Le recomendamos ingresar periódicamente a nuestra página web **www.sat.gob.pe** donde se publica la información sobre remates que realiza la entidad.

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []