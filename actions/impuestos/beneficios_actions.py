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


📋 **Requisitos:**
• Ser propietario de un solo predio (no sólo en el distrito).
• Su ingreso bruto debe estar constituido por la pensión y no exceder de 1 UIT mensual.
• Formato de solicitud (proporcionado por el SAT).
• Documento de identidad del titular o representante legal.
• Resolución o documento que otorga la calidad de pensionista.
• Última boleta de pago o liquidación de pensión.

**Para presentar tu solicitud:**
📍 Debes acercarte a nuestras oficinas del SAT con la documentación requerida

**¿Qué más necesitas?**  
• 'Menú principal' - Otras opciones
• 'Finalizar chat'"""

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

📋 **Requisitos:**
• Ser propietario de un solo predio (no sólo en el distrito) y tener de 60 años a más.
• Su ingreso bruto no debe exceder de 1 UIT mensual.
• Formato de solicitud (proporcionado por el SAT).
• Documento de identidad del titular o representante legal.
• Última boleta de pago, recibo por honorarios u otros que acrediten sus ingresos.
• Documentos adicionales que acrediten que no cuenta con la calidad de pensionista.

**Para presentar tu solicitud:**
📍 Debes acercarte a nuestras oficinas del SAT con la documentación requerida

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []