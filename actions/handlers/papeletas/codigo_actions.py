"""
Actions para consulta de códigos de falta
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from actions.api.sat_client import sat_client

logger = logging.getLogger(__name__)

class CodigoProcessor:
    """Procesador de códigos de falta"""

    @staticmethod
    def extract_codigo_from_message(tracker: Tracker) -> str:
        """
        Extrae código de falta del mensaje del usuario

        Returns:
            str: Código de falta o None si no se encuentra
        """
        entities = tracker.latest_message.get('entities', [])

        # Buscar en entities
        for entity in entities:
            if entity['entity'] == 'codigo_falta':
                return entity['value']

        # Buscar en el texto del mensaje
        texto = tracker.latest_message.get('text', '')
        codigo_match = re.search(r'\b[A-Z]\d{1,2}\b', texto.upper())
        if codigo_match:
            return codigo_match.group()

        return None

    @staticmethod
    def validate_and_clean_codigo(codigo: str) -> tuple[bool, str]:
        """
        Valida y limpia código de falta

        Returns:
            tuple: (es_valido, codigo_limpio)
        """
        if not codigo:
            return False, ""

        # Limpiar código
        codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo.strip().upper())

        # Patrones válidos para códigos de falta
        patrones_validos = [
            r'^[A-Z]\d{1,2}$',  # A5, C15, M08
            r'^\d{3}$',         # 001, 125 (menos común)
        ]

        es_valido = any(re.match(patron, codigo_limpio) for patron in patrones_validos)
        return es_valido, codigo_limpio

class ActionConsultarCodigoFalta(Action):
    """Action simplificado para consulta directa de códigos de falta"""

    def name(self) -> Text:
        return "action_consultar_codigo_falta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de código de falta")

        # 1. Extraer código del mensaje
        codigo = CodigoProcessor.extract_codigo_from_message(tracker)

        if not codigo:
            return self._request_codigo(dispatcher)

        # 2. Validar formato
        es_valido, codigo_limpio = CodigoProcessor.validate_and_clean_codigo(codigo)

        if not es_valido:
            return self._handle_invalid_codigo(dispatcher, codigo)

        # 3. Ejecutar consulta API directamente
        logger.info(f"Consultando código: {codigo_limpio}")
        return self._execute_codigo_api_query(dispatcher, codigo_limpio)

    def _execute_codigo_api_query(self, dispatcher: CollectingDispatcher,
                                 codigo: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API de códigos"""

        dispatcher.utter_message(text=f"🔍 Consultando información del código **{codigo}**...")

        try:
            resultado = sat_client.consultar_codigo_falta(codigo)

            if resultado and isinstance(resultado, dict) and resultado:
                message = self._format_codigo_response(resultado, codigo)
                dispatcher.utter_message(text=message)
            elif isinstance(resultado, list) and len(resultado) > 0:
                message = self._format_codigo_response(resultado[0], codigo)
                dispatcher.utter_message(text=message)
            else:
                self._handle_codigo_not_found(dispatcher, codigo)

        except Exception as e:
            logger.error(f"Error en consulta API de código: {e}")
            self._handle_api_error(dispatcher, codigo)

        return [SlotSet("ultimo_documento", codigo)]

    def _format_codigo_response(self, data: Dict[str, Any], codigo: str) -> str:
        """Formatea la respuesta de la API de códigos"""

        # Mapear campos de la API real
        codigo_falta = data.get('ccodfal', codigo).strip() if data.get('ccodfal') else codigo
        infraccion = data.get('vdesfal', 'No disponible').strip() if data.get('vdesfal') else 'No disponible'
        calificacion = data.get('cnivGra', 'No disponible').strip() if data.get('cnivGra') else 'No disponible'
        porcentaje_uit = data.get('nporUIT', 'No disponible')
        monto = data.get('nmonto', 'No disponible')
        sancion = data.get('vdesSan', 'No disponible').strip() if data.get('vdesSan') else 'No disponible'
        puntos = data.get('siPuntos', 'No disponible')
        medida_preventiva = data.get('vdesMAc', 'No disponible').strip() if data.get('vdesMAc') else 'No disponible'

        # Formatear valores numéricos
        if isinstance(porcentaje_uit, (int, float)):
            porcentaje_uit = f"{porcentaje_uit}%"

        if isinstance(monto, (int, float)):
            monto = f"{monto:.2f}"

        if isinstance(puntos, (int, float)):
            puntos = f"{int(puntos)} puntos"

        message = f"""📋 **Información del código {codigo_falta}:**

**🚨 INFRACCIÓN:** {infraccion}
**📊 CALIFICACIÓN:** {calificacion}
**💰 %UIT:** {porcentaje_uit}
**💵 MONTO:** S/ {monto}
**⚖️ SANCIÓN:** {sancion}
**⭐ PUNTOS:** {puntos}
**🚫 MEDIDA PREVENTIVA:** {medida_preventiva}

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'

📌 **Más información en:**
https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx"""

        return message

    def _request_codigo(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita código cuando no se proporcionó"""

        message = """Para consultar un código de infracción, necesito el código específico.

📝 **Ejemplos de códigos:**
• G40, M08, A05, G25

**Ejemplos de cómo preguntar:**
• "¿Qué significa G40?"
• "Código M08"

¿Cuál es el código que quieres consultar?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_codigo(self, dispatcher: CollectingDispatcher,
                              codigo: str) -> List[Dict[Text, Any]]:
        """Maneja códigos con formato inválido"""

        message = f"""❌ El código **{codigo}** no tiene un formato válido.

📝 **Formato correcto:**
• Una letra seguida de 1-2 números
• Ejemplos: G40, M08, A05

Por favor, proporciona un código válido."""

        dispatcher.utter_message(text=message)
        return []

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

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)

    def _handle_api_error(self, dispatcher: CollectingDispatcher, codigo: str):
        """Maneja errores de la API"""

        message = f"""😔 Lo siento, tuve un problema técnico al consultar el código **{codigo}**.

🔧 **Esto puede ocurrir por:**
• Mantenimiento del sistema del SAT
• Problemas temporales de conexión

📱 **Mientras tanto puedes:**
• Consultar directamente en: https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx
• Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
• Intentar con otro código
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)