"""
Actions para declare y liquide sus impuestos
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionDeclaracionImpuestoVehicular(Action):
    """Action para declaración de impuesto vehicular"""

    def name(self) -> Text:
        return "action_declaracion_impuesto_vehicular"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de declaración impuesto vehicular")

        message = """🚗 **DECLARACIÓN IMPUESTO VEHICULAR**

**Requisitos necesarios:**
• Documento de identidad del propietario o representante
• Último recibo de luz, agua o teléfono del domicilio del propietario
• Tarjeta de Identificación Vehicular y copia simple
• Original y copia de factura, boleta de venta, acta de transferencia o DUA

**En caso de representación:**
• Poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT

🔗 **Más información:**
https://www.sat.gob.pe/websitev9/TributosMultas/ImpuestoVehicular/Informacion

**💻 OPCIÓN ONLINE:**
🔗 **Agencia Virtual SAT:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**Pasos online:**
1. Registrarse en Agencia Virtual
2. Ingresar en la opción "Inscripción Vehicular"
3. Completar formulario online

📖 **Guía interactiva:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Qué más necesitas?**
• 'Consultar deuda vehicular' - Ver si tienes deuda pendiente
• 'Declaración predial' - Para inmuebles
• 'Oficinas SAT' - Ubicaciones para trámite presencial
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionLiquidacionAlcabala(Action):
    """Action para liquidación de alcabala"""

    def name(self) -> Text:
        return "action_liquidacion_alcabala"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de liquidación de alcabala")

        message = """🏠 **LIQUIDACIÓN DE ALCABALA**

**Requisitos necesarios:**
• Documento de identidad de la persona que realice el trámite
• Copia simple del documento en el que consta la transferencia de propiedad
• Copia simple del autovalúo del año en que se produjo la transferencia (solo si el predio no está en el Cercado ni inscrito en el SAT)

🔗 **Más información:**
https://www.sat.gob.pe/websitev9/TributosMultas/ImpuestoAlcabala/Informacion

**💻 OPCIÓN ONLINE:**
🔗 **Agencia Virtual SAT:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**Pasos online:**
1. Registrarse en Agencia Virtual
2. Ingresar en la opción "Liquidación de Alcabala"
3. Completar formulario online

📖 **Guía interactiva:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Qué es la alcabala?**
Es el impuesto que grava las transferencias de propiedad de bienes inmuebles urbanos y rústicos.

**¿Qué más necesitas?**
• 'Declaración predial' - Para registrar nuevo predio
• 'Consultar deuda' - Ver si tienes deuda pendiente
• 'Oficinas SAT' - Ubicaciones para trámite presencial
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionDeclaracionImpuestoPredial(Action):
    """Action para declaración de impuesto predial"""

    def name(self) -> Text:
        return "action_declaracion_impuesto_predial"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de declaración impuesto predial")

        message = """🏠 **DECLARACIÓN IMPUESTO PREDIAL**

**Requisitos necesarios:**
• Documento de identidad del propietario o representante
• Último recibo de luz, agua o teléfono del domicilio del actual propietario
• Documento que sustenta la adquisición o compra: Minuta o transferencia

**En caso de representación:**
• Poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT

🔗 **Más información:**
https://www.sat.gob.pe/websitev9/TributosMultas/PredialyArbitrios/Informacion

**💻 OPCIÓN ONLINE:**
🔗 **Agencia Virtual SAT:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**Pasos online:**
1. Registrarse en Agencia Virtual
2. Ingresar en la opción "Inscripción Predial"
3. Completar formulario de inscripción

📖 **Guía interactiva:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Cuándo declarar?**
• Cuando adquieres un predio nuevo
• Cuando haces mejoras significativas
• Cuando cambia el uso del predio

**¿Qué más necesitas?**
• 'Consultar deuda predial' - Ver si tienes deuda pendiente
• 'Declaración vehicular' - Para vehículos
• 'Oficinas SAT' - Ubicaciones para trámite presencial
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionFraccionarDeuda(Action):
    """Action para fraccionar deuda tributaria"""

    def name(self) -> Text:
        return "action_fraccionar_deuda"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información para fraccionar deuda")

        message = """💰 **FRACCIONAR DEUDA TRIBUTARIA**

Para pagar tu deuda tributaria en cuotas:

🔗 **Agencia Virtual SAT:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**Pasos:**
1. Registrarse en Agencia Virtual
2. Ingresar en la opción "Facilidades de pago"
3. Seleccionar las deudas que deseas fraccionar
4. Elegir número de cuotas
5. Confirmar el compromiso de pago

⚠️ **IMPORTANTE - Requisito obligatorio:**
Primero inscríbete en la Casilla Electrónica del MTC:
📌 https://casilla.mtc.gob.pe/#/registro
📋 Base Legal: R. Directoral N°023-2024-MTC/18

📖 **Guía interactiva:**
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**Beneficios del fraccionamiento:**
• Pagar en cuotas mensuales cómodas
• Evitar intereses adicionales si cumples el cronograma
• Mantener tu historial crediticio al día

**¿Qué más necesitas?**
• 'Consultar deuda' - Ver cuánto debes exactamente
• 'Casilla MTC' - Información del registro obligatorio
• 'Cómo pago' - Otras formas de pago
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []