"""
Actions para información de lugares y pagos (respuestas simples)
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionLugaresAgenciasHorarios(Action):
    """Action para mostrar agencias y horarios del SAT"""

    def name(self) -> Text:
        return "action_lugares_agencias_horarios"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de agencias y horarios")

        message = """🏫 **AGENCIAS Y HORARIOS**

Nuestros **centros de atención y lugares de pago** son:

🏫 **Oficina Principal**
📍 Jr. Camaná 370, Cercado de Lima
🕐 Lunes a viernes: 8:00am - 5:00pm
🕐 Sábados: 9:00am - 1:00pm

🏫 **Agencia Argentina**
📍 Av. Argentina 2926, Lima
🕐 Lunes a viernes: 8:00am - 5:00pm
🕐 Sábados: 9:00am - 1:00pm

🏫 **Agencia San Juan de Miraflores**
📍 Av. De los Héroes 638-A, San Juan de Miraflores
🕐 Lunes a viernes: 8:00am - 5:00pm
🕐 Sábados: 9:00am - 1:00pm

🏫 **Agencia Centro Comercial Plaza Camacho**
📍 Tienda comercial 916 – Planta baja
Av. Javier Prado Este 5193, La Molina
🕐 Lunes a viernes: 9:00am - 6:00pm
🕐 Sábados: 9:00am - 1:00pm

🏫 **Centro MAC de Lima Norte**
📍 Mall Plaza de Comas, Av. Los Ángeles 602, Sótano 1
Urb. El Álamo – Comas
🕐 Lunes a viernes: 8:30am - 6:00pm
🕐 Sábados: 8:30am - 1:00pm

**Servicios disponibles:**
• Operaciones, consultas y facilidades de pago
• Deuda tributaria (Impuesto Vehicular, Alcabala)
• Deuda no tributaria (Infracciones de tránsito)

💳 **Atención de Caja:** Solo tarjeta débito/crédito (no efectivo) o vía web

🔗 **Más información:** https://www.sat.gob.pe/websitev9/Contactenos/AgenciasSAT

**¿Qué más necesitas?**
• 'Lugares de pago' - Dónde puedes pagar
• 'Formas de pago' - Cómo puedes pagar
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionLugaresPago(Action):
    """Action para mostrar lugares donde se puede pagar"""

    def name(self) -> Text:
        return "action_lugares_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de lugares de pago")

        message = """💰 **LUGARES DE PAGO**

Puede pagar sus tributos y multas en:

🌐 **Portal Web del SAT:**
• www.sat.gob.pe
• Tarjetas: Visa, Mastercard, American Express
• Yape

🏦 **Bancos y Entidades Financieras:**
• BCP
• INTERBANK  
• BBVA
• SCOTIABANK
• BANBIF
• Caja Metropolitana
• Western Union

**Modalidades bancarias:**
• Agentes autorizados
• Banca móvil
• Banca por internet

🏢 **Oficinas del SAT:**
• Tarjetas: Visa, Mastercard, American Express, Diners Club
• Dinero en efectivo
• Cheque de gerencia o certificado a nombre de "Servicio de Administración Tributaria de Lima"

🔗 **Guía completa:** https://www.sat.gob.pe/WebSiteV9/Inicio/AyudaPagos/FormasLugaresPago

**¿Qué más necesitas?**
• 'Agencias y horarios' - Ubicaciones y horarios de oficinas
• 'Formas de pago' - Opciones específicas de pago
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionLugaresFormasPago(Action):
    """Action para mostrar opciones de formas de pago"""

    def name(self) -> Text:
        return "action_lugares_formas_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando opciones de formas de pago")

        message = """💳 **FORMAS DE PAGO - OPCIONES**

¿Qué tipo de pago necesitas?

📋 **OPCIONES DISPONIBLES:**
• **"Pagos en línea"** - Pagar inmediatamente por internet
• **"Compromiso de pago"** - Facilidades de pago y fraccionamiento  
• **"Fraccionar deuda"** - Dividir tu deuda en cuotas

💡 **También puedes decir:**
• "Cómo pago por internet"
• "Quiero facilidades de pago"
• "Pagar en cuotas"

¿Qué opción necesitas?"""

        dispatcher.utter_message(text=message)
        return []