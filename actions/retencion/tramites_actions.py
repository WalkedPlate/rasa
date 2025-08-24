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

📧 **Correo:** asuservicio@sat.gob.pe

**Datos a incluir en el correo:**
• Nombres y apellidos completos
• Número de DNI
• Número de expediente coactivo

**Proceso:**
1. Realizar el pago de la deuda pendiente
2. Enviar correo con los datos solicitados
3. Esperar confirmación del levantamiento

**¿Qué más necesitas?**
• 'Orden de captura' - Consultar si tu vehículo tiene orden de captura
• 'Suspender cobranza' - Solicitar suspensión de cobranza coactiva
• 'Cómo pago' - Información de pagos
• 'Menú principal' - Otras opciones"""

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

**En el enlace selecciona:**
• Opción "Internamiento de vehículo"
• Ingresa los datos solicitados
• Consulta el estado de tu vehículo

**¿Qué información encontrarás?**
• Estado actual del vehículo
• Ubicación del depósito (si aplica)
• Procedimientos para retiro
• Costos asociados

**¿Qué más necesitas?**
• 'Orden de captura' - Consultar órdenes de captura
• 'Levantamiento' - Solicitar levantamiento de medida cautelar
• 'Menú principal' - Otras opciones"""

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

🔗 **Directiva completa:**
https://www.sat.gob.pe/WebSiteV8/Modulos/documentos/TUPA/Directiva_001-006-000000023_aprobada_por_RJ_001-004-00003951.pdf

🔗 **Descarga y consulta del formato:**
https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

🔗 **Mesa de Partes Digital:**
https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Levantamiento' - Solicitar levantamiento de medida cautelar
• 'Tercería' - Trámite de tercería de propiedad
• 'Menú principal' - Otras opciones"""

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

Para verificar los requisitos y procedimientos:

🔗 **Requisitos detallados:**
https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA

🔗 **Descarga y consulta del formato:**
https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

🔗 **Presentación del trámite:**
Mesa de Partes Digital: https://www.sat.gob.pe/MesaPartesDigital

**¿Qué es la tercería de propiedad?**
Procedimiento legal mediante el cual una persona acredita ser propietario de un bien que ha sido embargado por deudas ajenas.

**Casos típicos:**
• El bien embargado no pertenece al deudor
• Existe documentación que acredita la propiedad del tercero
• Se requiere levantar la medida cautelar sobre el bien

**¿Qué más necesitas?**
• 'Levantamiento' - Solicitar levantamiento de medida cautelar
• 'Suspender cobranza' - Suspensión de cobranza coactiva
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionRetencionLevantamiento(Action):
    """Action para levantamiento de medida cautelar"""

    def name(self) -> Text:
        return "action_retencion_levantamiento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de levantamiento de medida cautelar")

        message = """🔓 **SOLICITAR LEVANTAMIENTO DE MEDIDA CAUTELAR**

Para solicitar el levantamiento de medidas cautelares:

🔗 **Requisitos detallados:**
https://www.sat.gob.pe/WebSiteV8/Modulos/documentos/TUPA/Directiva_001-006-000000023_aprobada_por_RJ_001-004-00003951.pdf

🔗 **Descarga y consulta del formato:**
https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

🔗 **Presentación del trámite:**
Mesa de Partes Digital: https://www.sat.gob.pe/MesaPartesDigital

**¿Qué medidas cautelares se pueden levantar?**
• Embargo de cuentas bancarias
• Retención de fondos
• Orden de captura vehicular
• Internamiento de vehículos
• Inscripción de embargo en registros públicos

**Requisitos generales:**
• Pago de la deuda o acuerdo de facilidades
• Presentación de garantías suficientes
• Cumplimiento de procedimientos establecidos

**¿Qué más necesitas?**
• 'Tercería' - Trámite de tercería de propiedad
• 'Suspender cobranza' - Suspensión de cobranza coactiva
• 'Cómo pago' - Información de pagos
• 'Menú principal' - Otras opciones"""

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

Para enterarse sobre próximos remates vehiculares:

🌐 **Página web oficial:**
Le recomendamos ingresar periódicamente a nuestra página web **www.sat.gob.pe** donde se publica la información sobre remates que realiza la entidad.

**¿Qué más necesitas?**
• 'Orden de captura' - Consultar si tu vehículo tiene orden de captura
• 'Levantamiento' - Solicitar levantamiento de medida cautelar
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []