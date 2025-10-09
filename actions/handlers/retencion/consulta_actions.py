"""
Actions para consulta de órdenes de captura
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from actions.api.sat_client import sat_client

logger = logging.getLogger(__name__)

class DocumentProcessorRetencion:
    """Procesador de documentos para consultas de retención"""

    @staticmethod
    def extract_placa_from_message(tracker: Tracker) -> str:
        """
        Extrae placa del mensaje del usuario

        Returns:
            str: Placa vehicular o None si no se encuentra
        """
        entities = tracker.latest_message.get('entities', [])

        # Buscar en entities
        for entity in entities:
            if entity['entity'] == 'placa':
                return entity['value']

        # Buscar en el texto del mensaje
        texto = tracker.latest_message.get('text', '')
        placa_match = re.search(r'[A-Z]{2,3}\d{3,4}|[A-Z]\d[A-Z]\d{3}|U\d[A-Z]\d{3}', texto.upper())
        if placa_match:
            return placa_match.group()

        return None

    @staticmethod
    def validate_placa(placa: str) -> tuple[bool, str]:
        """
        Valida formato de placa vehicular

        Returns:
            tuple: (es_valido, placa_limpia)
        """
        if not placa:
            return False, ""

        # Limpiar placa
        placa_limpia = re.sub(r'[^A-Z0-9]', '', placa.strip().upper())

        # Patrones válidos de placas peruanas
        patrones_validos = [
            r'^[A-Z]{3}\d{3}$',      # ABC123
            r'^[A-Z]{2}\d{4}$',      # AB1234
            r'^[A-Z]\d[A-Z]\d{3}$',  # A1B234
            r'^U\d[A-Z]\d{3}$',      # U1A710
            r'^[TSD][A-Z]{2}\d{3}$', # T1C567
        ]

        es_valida = any(re.match(patron, placa_limpia) for patron in patrones_validos)
        return es_valida, placa_limpia

class ActionConsultarOrdenCaptura(Action):
    """Action para consultar órdenes de captura por placa"""

    def name(self) -> Text:
        return "action_consultar_orden_captura"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de orden de captura")

        # 1. Extraer placa del mensaje
        placa = DocumentProcessorRetencion.extract_placa_from_message(tracker)

        if not placa:
            return self._request_placa(dispatcher)

        # 2. Validar formato
        es_valida, placa_limpia = DocumentProcessorRetencion.validate_placa(placa)

        if not es_valida:
            return self._handle_invalid_placa(dispatcher, placa)

        # 3. Ejecutar consulta API
        logger.info(f"Consultando orden de captura para placa: {placa_limpia}")
        return self._execute_api_query(dispatcher, placa_limpia)

    def _execute_api_query(self, dispatcher: CollectingDispatcher,
                          placa: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API de órdenes de captura"""

        dispatcher.utter_message(text=f"🔍 Consultando órdenes de captura para placa **{placa}**...")

        try:
            resultado = sat_client.consultar_orden_captura_por_placa(placa)

            if resultado is not None:
                message = self._format_captura_response(resultado, placa)
                dispatcher.utter_message(text=message)
            else:
                self._handle_api_error(dispatcher, placa)

        except Exception as e:
            logger.error(f"Error en consulta API de orden de captura: {e}")
            self._handle_api_error(dispatcher, placa)

        return [SlotSet("ultimo_documento", placa)]

    def _format_captura_response(self, data: Dict[str, Any], placa: str) -> str:
        """Formatea la respuesta de órdenes de captura"""

        body_count = data.get("bodyCount", 0)
        ordenes = data.get("data", [])

        if body_count == 0 or not ordenes:
            return f"""✅ **¡Buenas noticias!** Su vehículo con placa **{placa}** NO tiene órdenes de captura activas.

🚗 Su vehículo no presenta restricciones por órdenes de captura.

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        cantidad = len(ordenes)
        total = sum(float(orden.get('monto', 0)) for orden in ordenes)

        # Si hay muchas órdenes, mostrar solo las primeras y referir al link
        if cantidad > 3:
            message = f"""🚨 **ALERTA: Su vehículo placa {placa} tiene {cantidad} órdenes de captura activas**

⚠️ **Primeras 3 órdenes:**

"""
            ordenes_mostrar = ordenes[:3]
        else:
            message = f"""🚨 **ALERTA: Su vehículo placa {placa} tiene {cantidad} orden{'es' if cantidad > 1 else ''} de captura activa{'s' if cantidad > 1 else ''}**

"""
            ordenes_mostrar = ordenes

        # Mostrar detalles de cada orden
        for i, orden in enumerate(ordenes_mostrar, 1):
            concepto = orden.get('ctributo', 'No especificado').strip()
            documento = orden.get('cnumDoc', 'No especificado').strip()
            monto = float(orden.get('monto', 0))
            placa_original = orden.get('cplaOri', placa).strip()

            message += f"📋 **Orden #{i}:**\n"
            message += f"• **Documento:** {documento}\n"
            message += f"• **Concepto:** {concepto}\n"
            message += f"• **Placa original:** {placa_original}\n"
            message += f"• **Monto:** S/ {monto:,.2f}\n\n"

        if cantidad > 3:
            message += f"... y {cantidad - 3} orden{'es' if cantidad - 3 > 1 else ''} más.\n\n"

        message += f"💰 **Total adeudado:** S/ {total:,.2f}\n\n"

        message += "📌 **Mayor detalle en:**\n"
        message += "https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=7\n\n"

        # Recomendaciones según cantidad
        if cantidad > 5:
            message += "Ingrese a la página web:\n"
            message += "https://www.sat.gob.pe/VirtualSAT/principal.aspx?mysession=pquJ7myzyT7AtQ4GWcIHxzs8BioTAJmrZG%2fJsgO0%2bEs%3d\n\n"

        message += "**¿Qué más necesitas?**\n"
        message += "• 'Menú principal' - Otras opciones\n"
        message += "• 'Finalizar chat'\n\n"

        return message

    def _request_placa(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita placa cuando no se proporcionó"""

        message = """Para consultar órdenes de captura necesito la placa del vehículo.

🚗 **Formato de placa válido:**
• ABC123 
• U1A710
• DEF456, GHI789, etc.

¿Cuál es la placa del vehículo a consultar?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_placa(self, dispatcher: CollectingDispatcher,
                             placa: str) -> List[Dict[Text, Any]]:
        """Maneja placas con formato inválido"""

        message = f"""❌ La placa **{placa}** no tiene un formato válido.

**Formatos correctos:**
• ABC123 (clásico)
• U1A710 (nuevo formato)
• DEF456, GHI789, etc.

Por favor, proporciona una placa válida."""

        dispatcher.utter_message(text=message)
        return []

    def _handle_api_error(self, dispatcher: CollectingDispatcher, placa: str):
        """Maneja errores de la API"""

        message = f"""😔 Lo siento, tuve un problema técnico al consultar la placa **{placa}**.

🔧 **Esto puede ocurrir por:**
• Mantenimiento del sistema del SAT
• Problemas temporales de conexión

📱 **Mientras tanto puedes:**
• Consultar directamente en: https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=7
• Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
• Intentar con otra placa
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)