"""
Actions para beneficios tributarios
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionBeneficiosPensionista(Action):
    """Action para beneficios tributarios para pensionistas"""

    def name(self) -> Text:
        return "action_beneficios_pensionista"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de beneficios para pensionistas")

        message = """👴 **BENEFICIOS TRIBUTARIOS - PENSIONISTAS**

Los pensionistas pueden acceder a beneficios especiales en el pago de impuestos.

📋 **Requisitos y más información:**
https://www.sat.gob.pe/WebSiteV8/Modulos/documentos/TUPA/Directiva_001-006-000000023_aprobada_por_RJ_001-004-00003951.pdf

**¿Qué beneficios incluye?**
• Descuentos en impuesto predial
• Facilidades de pago especiales
• Exoneraciones parciales según el caso

**Para presentar tu solicitud:**
📍 Debes acercarte a nuestras oficinas del SAT con la documentación requerida

🏢 **Oficinas del SAT:**
• **Oficina Principal:** Jr. Camaná 370, Cercado de Lima
• **Agencia Argentina:** Av. Argentina 2926, Lima
• **Agencia San Juan de Miraflores:** Av. De los Héroes 638-A

**Horarios:**
• Lunes a viernes: 8:00am a 5:00pm
• Sábados: 9:00am a 1:00pm

**¿Qué más necesitas?**  
• 'Beneficios adulto mayor' - Para adultos mayores no pensionistas
• 'Oficinas SAT' - Ubicaciones y horarios detallados
• 'Consultar deuda' - Ver tu situación tributaria actual
• 'Menú principal' - Otras opciones

💡 **Tip:** Lleva toda la documentación que acredite tu condición de pensionista."""

        dispatcher.utter_message(text=message)
        return []


class ActionBeneficiosAdultoMayor(Action):
    """Action para beneficios tributarios para adultos mayores no pensionistas"""

    def name(self) -> Text:
        return "action_beneficios_adulto_mayor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de beneficios para adultos mayores no pensionistas")

        message = """👵 **BENEFICIOS TRIBUTARIOS - ADULTO MAYOR NO PENSIONISTA**

Los adultos mayores no pensionistas también pueden acceder a beneficios tributarios especiales.

📋 **Requisitos y más información:**
https://www.sat.gob.pe/WebSiteV8/Modulos/documentos/TUPA/Directiva_001-006-000000023_aprobada_por_RJ_001-004-00003951.pdf

**¿Qué beneficios incluye?**
• Descuentos en impuesto predial según edad y condición socioeconómica
• Facilidades de pago adaptadas a tu situación
• Exoneraciones parciales en casos específicos

**¿Quiénes califican?**
• Personas mayores de 60 años
• Que no reciban pensión de jubilación
• Que cumplan con requisitos socioeconómicos específicos

**Para presentar tu solicitud:**
📍 Debes acercarte a nuestras oficinas del SAT con la documentación requerida

🏢 **Oficinas del SAT:**
• **Oficina Principal:** Jr. Camaná 370, Cercado de Lima
• **Agencia Argentina:** Av. Argentina 2926, Lima  
• **Agencia San Juan de Miraflores:** Av. De los Héroes 638-A

**Horarios:**
• Lunes a viernes: 8:00am a 5:00pm
• Sábados: 9:00am a 1:00pm

**¿Qué más necesitas?**
• 'Beneficios pensionista' - Para pensionistas
• 'Oficinas SAT' - Ubicaciones y horarios detallados
• 'Consultar deuda' - Ver tu situación tributaria actual
• 'Menú principal' - Otras opciones

💡 **Tip:** La evaluación socioeconómica se realiza en la oficina según tu situación particular."""

        dispatcher.utter_message(text=message)
        return []