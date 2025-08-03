"""
Actions para consulta de códigos de falta con API del SAT
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from ..core.sat_api_client import sat_client

logger = logging.getLogger(__name__)

class CodigoValidator:
    """Validador de códigos de falta"""

    @staticmethod
    def clean_codigo(codigo: str) -> str:
        """Limpia y normaliza el código de falta"""
        if not codigo:
            return ""
        return re.sub(r'[^A-Z0-9]', '', codigo.strip().upper())

    @staticmethod
    def is_valid_codigo(codigo: str) -> bool:
        """Valida formato de código de falta"""
        if not codigo:
            return False

        patterns = [
            r'^[A-Z][0-9]{1,2}$',  # A5, C15, M08
            r'^[0-9]{3}$',         # 001, 125
        ]

        return any(re.match(pattern, codigo) for pattern in patterns)

class ActionConsultarCodigoFalta(Action):
    """Action para consulta de códigos de falta"""

    def name(self) -> Text:
        return "action_consultar_codigo_falta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de código de falta")

        confirmacion_pendiente = tracker.get_slot("confirmacion_pendiente")

        if confirmacion_pendiente:
            return self._process_confirmation(dispatcher, tracker)
        else:
            return self._validate_and_confirm_codigo(dispatcher, tracker)

    def _validate_and_confirm_codigo(self, dispatcher: CollectingDispatcher,
                                    tracker: Tracker) -> List[Dict[Text, Any]]:
        """Valida código y solicita confirmación"""

        entities = tracker.latest_message.get('entities', [])
        codigo = None

        for entity in entities:
            if entity['entity'] == 'codigo_falta':
                codigo = entity['value']
                break

        if not codigo:
            codigo = tracker.get_slot("codigo_falta")

        if not codigo:
            return self._request_codigo(dispatcher)

        codigo_limpio = CodigoValidator.clean_codigo(codigo)

        if not CodigoValidator.is_valid_codigo(codigo_limpio):
            return self._handle_invalid_codigo(dispatcher, codigo)

        logger.info(f"Código válido detectado: {codigo_limpio}")

        message = f"Detecté el código de falta **{codigo_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=message)

        return [
            SlotSet("codigo_falta", codigo_limpio),
            SlotSet("confirmacion_pendiente", True),
            SlotSet("opcion_actual", "codigo_falta")
        ]

    def _process_confirmation(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker) -> List[Dict[Text, Any]]:
        """Procesa la confirmación del usuario"""

        intent = tracker.latest_message['intent']['name']

        if intent == "confirm_yes":
            return self._execute_codigo_api_query(dispatcher, tracker)
        elif intent == "confirm_no":
            return self._handle_codigo_correction(dispatcher)
        else:
            codigo = tracker.get_slot("codigo_falta")
            message = f"Para el código **{codigo}**, necesito que confirmes:\n\n✅ Di 'sí' si es correcto\n❌ Di 'no' si necesitas corregirlo"
            dispatcher.utter_message(text=message)
            return []

    def _execute_codigo_api_query(self, dispatcher: CollectingDispatcher,
                                 tracker: Tracker) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API de códigos"""

        codigo = tracker.get_slot("codigo_falta")

        dispatcher.utter_message(text=f"🔍 Consultando información del código **{codigo}**...")

        resultado = None
        try:
            resultado = sat_client.consultar_codigo_falta(codigo)
        except Exception as e:
            logger.error(f"Error en consulta API de código: {e}")

        if resultado and isinstance(resultado, dict) and resultado:
            message = self._format_codigo_response(resultado, codigo)
            dispatcher.utter_message(text=message)
        elif isinstance(resultado, list) and len(resultado) > 0:
            message = self._format_codigo_response(resultado[0], codigo)
            dispatcher.utter_message(text=message)
        else:
            self._handle_codigo_not_found(dispatcher, codigo)

        return self._reset_codigo_slots()

    def _request_codigo(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita código cuando no se proporcionó"""

        message = """Estimado ciudadano, indique el **CÓDIGO DE FALTA**:

📝 **Ejemplos de códigos:**
• C15, M08, A05, T12
• G25, F03, B20, L18

¿Cuál es el código que quieres consultar?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_codigo(self, dispatcher: CollectingDispatcher,
                              codigo: str) -> List[Dict[Text, Any]]:
        """Maneja códigos con formato inválido"""

        message = f"""❌ El código '{codigo}' no tiene un formato válido.

📝 **Formato correcto:**
• C15, M08, A05 (letra + números)
• T12, G25, F03, etc.

Por favor, proporciona un código válido."""

        dispatcher.utter_message(text=message)
        return []

    def _handle_codigo_correction(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Maneja cuando el usuario indica que el código es incorrecto"""

        message = """¿Cuál es el código correcto?

📝 **Recuerda el formato:**
• C15, M08, A05 (letra + números)
• T12, G25, F03, etc.

Por favor, proporciona el código correcto:"""

        dispatcher.utter_message(text=message)

        return [
            SlotSet("confirmacion_pendiente", False),
            SlotSet("codigo_falta", None)
        ]

    def _format_codigo_response(self, data: Dict[str, Any], codigo: str) -> str:
        """Formatea la respuesta de la API de códigos"""

        codigo_falta = data.get('codigo', codigo)
        infraccion = data.get('infraccion', 'No disponible')
        calificacion = data.get('calificacion', 'No disponible')
        porcentaje_uit = data.get('porcentaje_uit', 'No disponible')
        monto = data.get('monto', 'No disponible')
        sancion = data.get('sancion', 'No disponible')
        puntos = data.get('puntos', 'No disponible')
        medida_preventiva = data.get('medida_preventiva', 'No disponible')

        message = f"""📋 **Información del código {codigo_falta}:**

**🚨 INFRACCIÓN:** {infraccion}
**📊 CALIFICACIÓN:** {calificacion}
**💰 %UIT:** {porcentaje_uit}
**💵 MONTO:** S/ {monto}
**⚖️ SANCIÓN:** {sancion}
**⭐ PUNTOS:** {puntos}
**🚫 MEDIDA PREVENTIVA:** {medida_preventiva}

📌 **MAYOR DETALLE EN EL SIGUIENTE LINK:**
https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx"""

        return message

    def _handle_codigo_not_found(self, dispatcher: CollectingDispatcher, codigo: str):
        """Maneja cuando el código no se encuentra en la base de datos"""

        message = f"""❌ El código **{codigo}** no se encontró en la base de datos del SAT.

🔍 **Posibles causas:**
• El código puede estar mal escrito
• Podría ser un código desactualizado
• Puede que no exista ese código específico

💡 **Sugerencias:**
• Verifica que el código esté correctamente escrito
• Consulta directamente en: https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx
• Si tienes una papeleta física, verifica el código en el documento

¿Quieres intentar con otro código?"""

        dispatcher.utter_message(text=message)

    def _reset_codigo_slots(self) -> List[Dict[Text, Any]]:
        """Limpia slots después de completar consulta de código"""
        return [
            SlotSet("confirmacion_pendiente", False),
            SlotSet("codigo_falta", None),
            SlotSet("opcion_actual", None)
        ]