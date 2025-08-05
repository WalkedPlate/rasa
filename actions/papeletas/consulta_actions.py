"""
Actions para consulta de papeletas
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from ..core.sat_api_client import sat_client

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Procesador de documentos para consultas directas"""

    @staticmethod
    def extract_document_from_message(tracker: Tracker) -> tuple[str, str]:
        """
        Extrae documento y tipo del mensaje del usuario

        Returns:
            tuple: (documento, tipo) donde tipo es 'placa', 'dni', 'ruc' o None
        """
        entities = tracker.latest_message.get('entities', [])
        intent = tracker.latest_message.get('intent', {}).get('name', '')

        # Buscar en entities
        for entity in entities:
            if entity['entity'] == 'placa':
                return entity['value'], 'placa'
            elif entity['entity'] == 'dni':
                return entity['value'], 'dni'
            elif entity['entity'] == 'ruc':
                return entity['value'], 'ruc'

        # Inferir por intent
        if intent == 'consulta_rapida_placa':
            # Buscar patrón de placa en el texto
            texto = tracker.latest_message.get('text', '')
            placa_match = re.search(r'[A-Z]{2,3}\d{3,4}|[A-Z]\d[A-Z]\d{3}|U\d[A-Z]\d{3}', texto.upper())
            if placa_match:
                return placa_match.group(), 'placa'

        elif intent == 'consulta_rapida_dni':
            texto = tracker.latest_message.get('text', '')
            dni_match = re.search(r'\b\d{8}\b', texto)
            if dni_match:
                return dni_match.group(), 'dni'

        elif intent == 'consulta_rapida_ruc':
            texto = tracker.latest_message.get('text', '')
            ruc_match = re.search(r'\b[12]\d{10}\b', texto)
            if ruc_match:
                return ruc_match.group(), 'ruc'

        return None, None

    @staticmethod
    def validate_document(documento: str, tipo: str) -> tuple[bool, str]:
        """
        Valida formato de documento

        Returns:
            tuple: (es_valido, documento_limpio)
        """
        if not documento or not tipo:
            return False, ""

        documento_limpio = documento.strip().upper()

        if tipo == 'placa':
            # Limpiar placa
            documento_limpio = re.sub(r'[^A-Z0-9]', '', documento_limpio)

            # Patrones válidos de placas peruanas
            patrones_validos = [
                r'^[A-Z]{3}\d{3}$',      # ABC123
                r'^[A-Z]{2}\d{4}$',      # AB1234
                r'^[A-Z]\d[A-Z]\d{3}$',  # A1B234
                r'^U\d[A-Z]\d{3}$',      # U1A710
                r'^[TSD][A-Z]{2}\d{3}$', # T1C567
            ]

            es_valido = any(re.match(patron, documento_limpio) for patron in patrones_validos)
            return es_valido, documento_limpio

        elif tipo == 'dni':
            # Limpiar DNI
            documento_limpio = re.sub(r'[^0-9]', '', documento_limpio)
            es_valido = len(documento_limpio) == 8 and documento_limpio.isdigit()
            return es_valido, documento_limpio

        elif tipo == 'ruc':
            # Limpiar RUC
            documento_limpio = re.sub(r'[^0-9]', '', documento_limpio)
            es_valido = (len(documento_limpio) == 11 and
                        documento_limpio.isdigit() and
                        documento_limpio[0] in ['1', '2'])
            return es_valido, documento_limpio

        return False, ""

class ActionConsultarPapeletas(Action):
    """Action simplificado para consulta directa de papeletas"""

    def name(self) -> Text:
        return "action_consultar_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de papeletas")

        # 1. Extraer documento del mensaje
        documento, tipo = DocumentProcessor.extract_document_from_message(tracker)

        if not documento or not tipo:
            return self._request_document(dispatcher)

        # 2. Validar formato
        es_valido, documento_limpio = DocumentProcessor.validate_document(documento, tipo)

        if not es_valido:
            return self._handle_invalid_document(dispatcher, tipo, documento)

        # 3. Ejecutar consulta API directamente
        logger.info(f"Consultando {tipo}: {documento_limpio}")
        return self._execute_api_query(dispatcher, documento_limpio, tipo)

    def _execute_api_query(self, dispatcher: CollectingDispatcher,
                          documento: str, tipo: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API del SAT"""

        dispatcher.utter_message(text=f"🔍 Consultando papeletas para {tipo.upper()} **{documento}**...")

        try:
            # Llamar API según tipo
            if tipo == "placa":
                resultado = sat_client.consultar_papeletas_por_placa(documento)
            elif tipo == "dni":
                resultado = sat_client.consultar_papeletas_por_dni(documento)
            elif tipo == "ruc":
                resultado = sat_client.consultar_papeletas_por_ruc(documento)
            else:
                return self._handle_api_error(dispatcher, tipo, documento)

            # Procesar resultado
            if resultado is not None:
                message = self._format_papeletas_response(resultado, tipo, documento)
                dispatcher.utter_message(text=message)
            else:
                self._handle_api_error(dispatcher, tipo, documento)

        except Exception as e:
            logger.error(f"Error en consulta API: {e}")
            self._handle_api_error(dispatcher, tipo, documento)

        return [SlotSet("ultimo_documento", documento)]

    def _format_papeletas_response(self, data: Dict[str, Any],
                                  tipo: str, documento: str) -> str:
        """Formatea la respuesta de la API de papeletas"""

        body_count = data.get("bodyCount", 0)
        papeletas = data.get("data", [])

        if body_count == 0 or not papeletas:
            return f"""✅ **¡Excelente noticia!** No encontré papeletas pendientes para {tipo.upper()} **{documento}**.

🎉 Estás al día con las infracciones de tránsito.

**¿Qué más necesitas?**
• Dame otra placa/DNI/RUC para consultar
• 'Cómo pago' - Información de pagos
• 'Menú principal' - Otras opciones

💡 **Tip:** Si crees que deberías tener una papeleta, puedes registrarla manualmente."""

        cantidad = len(papeletas)
        total = sum(float(p.get('monto', 0)) for p in papeletas)

        message = f"📋 **Encontré {cantidad} papeleta{'s' if cantidad > 1 else ''} pendiente{'s' if cantidad > 1 else ''}** para {tipo.upper()} **{documento}**:\n\n"

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

        # Agregar recomendaciones según monto
        if total > 1000:
            message += "💡 **Recomendación:** El monto es elevado. Te sugiero solicitar facilidades de pago.\n\n"

        # Opciones contextuales
        message += "**¿Qué más necesitas?**\n"
        message += "• 'Cómo pago' - Información para pagar\n"
        message += "• 'Facilidades' - Pagar en cuotas\n"
        message += "• Dame otra placa/DNI/RUC para nueva consulta\n"
        message += "• 'Menú principal' - Otras opciones\n\n"

        message += "🏛️ *Consulta oficial del SAT de Lima*"

        return message

    def _request_document(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita documento cuando no se proporcionó información"""

        message = """Para consultar papeletas necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, APS583, U1A710
🆔 **Tu DNI** - 8 dígitos (ej: 12345678)
🏢 **RUC** - 11 dígitos (ej: 20123456789)

**Ejemplos de cómo escribir:**
• "Mi placa es APS583" o solo "APS583"
• "DNI 87654321" o solo "87654321"
• "RUC 20123456789"

¿Cuál puedes proporcionar?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_document(self, dispatcher: CollectingDispatcher,
                                tipo: str, documento: str) -> List[Dict[Text, Any]]:
        """Maneja documentos con formato inválido"""

        error_messages = {
            'placa': f"""❌ La placa **{documento}** no tiene un formato válido.

**Formatos correctos:**
• ABC123 (clásico)
• U1A710 (nuevo formato)
• DEF456, GHI789, etc.

Por favor, proporciona una placa válida.""",

            'dni': f"""❌ El DNI **{documento}** no es válido.

**Formato correcto:**
• Exactamente 8 dígitos
• Ejemplo: 12345678

Por favor, proporciona un DNI válido.""",

            'ruc': f"""❌ El RUC **{documento}** no es válido.

**Formato correcto:**
• Exactamente 11 dígitos
• Debe empezar con 1 o 2
• Ejemplo: 20123456789

Por favor, proporciona un RUC válido."""
        }

        message = error_messages.get(tipo, f"❌ El dato **{documento}** no es válido.")
        dispatcher.utter_message(text=message)
        return []

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

**¿Qué más necesitas?**
• Intentar con otro documento
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)