"""
Actions para consulta de papeletas con APIs del SAT
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from ..core.sat_api_client import sat_client

logger = logging.getLogger(__name__)

class DocumentValidator:
    """Validador de documentos de identificación"""

    @staticmethod
    def validate_and_clean_placa(placa: str) -> tuple[bool, str]:
        """Valida y limpia formato de placa vehicular"""
        if not placa:
            return False, ""
        placa_clean = re.sub(r'[^A-Z0-9]', '', placa.upper())
        is_valid = len(placa_clean) >= 6 and len(placa_clean) <= 7
        return is_valid, placa_clean

    @staticmethod
    def validate_and_clean_dni(dni: str) -> tuple[bool, str]:
        """Valida y limpia formato de DNI"""
        if not dni:
            return False, ""
        dni_clean = re.sub(r'[^0-9]', '', dni)
        is_valid = len(dni_clean) == 8
        return is_valid, dni_clean

    @staticmethod
    def validate_and_clean_ruc(ruc: str) -> tuple[bool, str]:
        """Valida y limpia formato de RUC"""
        if not ruc:
            return False, ""
        ruc_clean = re.sub(r'[^0-9]', '', ruc)
        is_valid = len(ruc_clean) == 11 and ruc_clean[0] in ['1', '2']
        return is_valid, ruc_clean

class ActionConsultarPapeletas(Action):
    """Action para manejo de consulta de papeletas con validación y confirmación"""

    def name(self) -> Text:
        return "action_consultar_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de papeletas")

        confirmacion_pendiente = tracker.get_slot("confirmacion_pendiente")

        if confirmacion_pendiente:
            return self._process_confirmation(dispatcher, tracker)
        else:
            return self._validate_and_confirm(dispatcher, tracker)

    def _validate_and_confirm(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker) -> List[Dict[Text, Any]]:
        """Valida documento proporcionado y solicita confirmación"""

        entities = tracker.latest_message.get('entities', [])

        documento = None
        tipo = None

        # Buscar datos en entities del mensaje actual
        for entity in entities:
            if entity['entity'] == 'placa':
                documento = entity['value']
                tipo = 'placa'
                break
            elif entity['entity'] == 'dni':
                documento = entity['value']
                tipo = 'dni'
                break
            elif entity['entity'] == 'ruc':
                documento = entity['value']
                tipo = 'ruc'
                break

        # Si no hay entities, verificar slots existentes
        if not documento:
            if tracker.get_slot("documento_consulta") and tracker.get_slot("tipo_documento"):
                documento = tracker.get_slot("documento_consulta")
                tipo = tracker.get_slot("tipo_documento")

        if not documento or not tipo:
            return self._request_document(dispatcher)

        # Validar según tipo de documento
        is_valid = False
        documento_limpio = ""

        if tipo == 'placa':
            is_valid, documento_limpio = DocumentValidator.validate_and_clean_placa(documento)
        elif tipo == 'dni':
            is_valid, documento_limpio = DocumentValidator.validate_and_clean_dni(documento)
        elif tipo == 'ruc':
            is_valid, documento_limpio = DocumentValidator.validate_and_clean_ruc(documento)

        if not is_valid:
            return self._handle_invalid_document(dispatcher, tipo, documento)

        logger.info(f"Documento válido detectado: {tipo} = {documento_limpio}")

        confirmation_message = f"Detecté el {tipo.upper()} **{documento_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=confirmation_message)

        return [
            SlotSet("documento_consulta", documento_limpio),
            SlotSet("tipo_documento", tipo),
            SlotSet("confirmacion_pendiente", True),
            SlotSet("opcion_actual", "papeletas")
        ]

    def _process_confirmation(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker) -> List[Dict[Text, Any]]:
        """Procesa la confirmación del usuario"""

        intent = tracker.latest_message['intent']['name']

        if intent == "confirm_yes":
            return self._execute_api_query(dispatcher, tracker)
        elif intent == "confirm_no":
            return self._handle_correction(dispatcher, tracker)
        else:
            tipo = tracker.get_slot("tipo_documento")
            documento = tracker.get_slot("documento_consulta")

            message = f"Para el {tipo} **{documento}**, necesito que confirmes:\n\n✅ Di 'sí' si es correcto\n❌ Di 'no' si necesitas corregirlo"
            dispatcher.utter_message(text=message)
            return []

    def _execute_api_query(self, dispatcher: CollectingDispatcher,
                          tracker: Tracker) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API del SAT"""

        documento = tracker.get_slot("documento_consulta")
        tipo = tracker.get_slot("tipo_documento")

        dispatcher.utter_message(text=f"🔍 Consultando papeletas para {tipo.upper()} **{documento}**...")

        resultado = None
        try:
            if tipo == "placa":
                resultado = sat_client.consultar_papeletas_por_placa(documento)
            elif tipo == "dni":
                resultado = sat_client.consultar_papeletas_por_dni(documento)
            elif tipo == "ruc":
                resultado = sat_client.consultar_papeletas_por_ruc(documento)
        except Exception as e:
            logger.error(f"Error en consulta API: {e}")

        if resultado is not None:
            message = self._format_papeletas_response(resultado, tipo, documento)
            dispatcher.utter_message(text=message)

            dispatcher.utter_message(
                text="\n💬 **¿Necesitas algo más?**\n"
                     "• 'Consultar con otro documento' para nueva consulta\n"
                     "• 'Pagos en línea' para información de pagos\n"
                     "• 'Finalizar' para cerrar"
            )
        else:
            self._handle_api_error(dispatcher, tipo, documento)

        return self._reset_slots()

    def _request_document(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita documento cuando no se proporcionó información"""

        message = """Para consultar papeletas necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, U1A710
🆔 **Tu DNI** - 8 dígitos
🏢 **RUC** - 11 dígitos

¿Cuál puedes proporcionar?"""

        dispatcher.utter_message(text=message)
        return self._reset_slots()

    def _handle_invalid_document(self, dispatcher: CollectingDispatcher,
                                tipo: str, documento: str) -> List[Dict[Text, Any]]:
        """Maneja documentos con formato inválido"""

        error_messages = {
            'placa': f"❌ La placa '{documento}' no tiene un formato válido.\n\n**Formatos correctos:** ABC123, U1A710, DEF456",
            'dni': f"❌ El DNI '{documento}' no es válido. Debe tener exactamente 8 dígitos.",
            'ruc': f"❌ El RUC '{documento}' no es válido. Debe tener 11 dígitos y empezar con 1 o 2."
        }

        message = error_messages.get(tipo, f"❌ El dato '{documento}' no es válido.")
        dispatcher.utter_message(text=message)

        return self._reset_slots()

    def _handle_correction(self, dispatcher: CollectingDispatcher,
                          tracker: Tracker) -> List[Dict[Text, Any]]:
        """Maneja cuando el usuario indica que el dato es incorrecto"""

        tipo = tracker.get_slot("tipo_documento")

        correction_messages = {
            'placa': "¿Cuál es la placa correcta? Por ejemplo: ABC123, U1A710",
            'dni': "¿Cuál es tu DNI correcto? Debe tener 8 dígitos.",
            'ruc': "¿Cuál es el RUC correcto? Debe tener 11 dígitos."
        }

        message = correction_messages.get(tipo, "¿Cuál es el dato correcto?")
        dispatcher.utter_message(text=message)

        return [
            SlotSet("confirmacion_pendiente", False),
            SlotSet("documento_consulta", None),
            SlotSet("tipo_documento", None)
        ]

    def _format_papeletas_response(self, data: Dict[str, Any],
                                  tipo: str, documento: str) -> str:
        """Formatea la respuesta de la API de papeletas"""

        body_count = data.get("bodyCount", 0)
        papeletas = data.get("data", [])

        if body_count == 0 or not papeletas:
            return f"""✅ ¡Excelente noticia! No encontré papeletas pendientes para {tipo.upper()} **{documento}**.

🎉 Estás al día con las infracciones de tránsito.

💡 **Tip:** Si crees que deberías tener una papeleta que no aparece, puedes registrarla manualmente en:
📌 https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=9&v=%20"""

        cantidad = len(papeletas)
        total = sum(float(p.get('monto', 0)) for p in papeletas)

        message = f"📋 Encontré **{cantidad} papeleta{'s' if cantidad > 1 else ''} pendiente{'s' if cantidad > 1 else ''}** para {tipo.upper()} **{documento}**:\n\n"

        # Mostrar hasta 3 papeletas para evitar mensajes muy largos
        for i, papeleta in enumerate(papeletas[:3], 1):
            falta = papeleta.get('falta', 'N/A').strip()
            doc_papeleta = papeleta.get('documento', 'N/A').strip()
            fecha = papeleta.get('fechainfraccion', 'N/A').strip()
            monto = float(papeleta.get('monto', 0))

            message += f"**🚨 Papeleta #{i}:**\n"
            message += f"• **Tipo de falta:** {falta}\n"
            message += f"• **N° papeleta:** {doc_papeleta}\n"
            message += f"• **Fecha:** {fecha}\n"
            message += f"• **Monto:** S/ {monto:.2f}\n\n"

        if cantidad > 3:
            message += f"... y {cantidad - 3} papeleta{'s' if cantidad - 3 > 1 else ''} más.\n\n"

        message += f"💰 **Total a pagar:** S/ {total:.2f}\n\n"

        if total > 1000:
            message += "💡 **Recomendación:** El monto es elevado. Te sugiero solicitar facilidades de pago.\n\n"

        message += "🔗 **¿Quieres pagar ahora?** Puedes hacerlo en:\n📌 https://www.sat.gob.pe/pagosenlinea/\n\n"
        message += "🏛️ *Consulta oficial del SAT de Lima*"

        return message

    def _handle_api_error(self, dispatcher: CollectingDispatcher,
                         tipo: str, documento: str):
        """Maneja errores de la API"""

        message = f"""😔 Lo siento, tuve un problema técnico al consultar {tipo.upper()} **{documento}**.

🔧 **Esto puede ocurrir por:**
• Mantenimiento del sistema del SAT
• Problemas temporales de conexión

📱 **Mientras tanto puedes:**
• Consultar directamente en: https://www.sat.gob.pe/pagosenlinea/
• Intentar nuevamente en unos minutos

⏰ ¿Quieres intentar con otro documento?"""

        dispatcher.utter_message(text=message)

    def _reset_slots(self) -> List[Dict[Text, Any]]:
        """Limpia slots después de completar la operación"""
        return [
            SlotSet("confirmacion_pendiente", False),
            SlotSet("documento_consulta", None),
            SlotSet("tipo_documento", None),
            SlotSet("opcion_actual", None)
        ]