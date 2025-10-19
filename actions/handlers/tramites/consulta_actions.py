"""
Actions para consulta de trámites administrativos
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from actions.api.sat_client import sat_client
from actions.utils.validators import validator

logger = logging.getLogger(__name__)


class TramiteProcessor:
    """Procesador de números de trámite"""

    @staticmethod
    def extract_numero_tramite_from_message(tracker: Tracker) -> str:
        """
        Extrae número de trámite del mensaje del usuario

        Returns:
            str: Número de trámite o None si no se encuentra
        """
        entities = tracker.latest_message.get('entities', [])

        # Buscar en entities
        for entity in entities:
            if entity['entity'] == 'numero_tramite':
                return entity['value']

        # Buscar en el texto del mensaje
        texto = tracker.latest_message.get('text', '')
        # Buscar secuencia de exactamente 14 dígitos
        tramite_match = re.search(r'\b\d{14}\b', texto)
        if tramite_match:
            return tramite_match.group()

        return None

    @staticmethod
    def validate_numero_tramite(numero: str) -> tuple[bool, str]:
        """
        Valida formato de número de trámite usando el validador core

        Returns:
            tuple: (es_valido, numero_limpio)
        """
        return validator.validate_numero_tramite(numero)


class ActionConsultarTramite(Action):
    """Action para consultar estado de trámite administrativo"""

    def name(self) -> Text:
        return "action_consultar_tramite"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de trámite administrativo")

        # 1. Extraer número de trámite del mensaje
        numero_tramite = TramiteProcessor.extract_numero_tramite_from_message(tracker)

        if not numero_tramite:
            return self._request_numero_tramite(dispatcher)

        # 2. Validar formato
        es_valido, numero_limpio = TramiteProcessor.validate_numero_tramite(numero_tramite)

        if not es_valido:
            return self._handle_invalid_numero(dispatcher, numero_tramite)

        # 3. Ejecutar consulta API
        logger.info(f"Consultando trámite: {numero_limpio}")
        return self._execute_tramite_api_query(dispatcher, numero_limpio)

    def _execute_tramite_api_query(self, dispatcher: CollectingDispatcher,
                                   numero_tramite: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API de trámites"""

        dispatcher.utter_message(text=f"🔍 Consultando estado del trámite **{numero_tramite}**...")

        try:
            resultado = sat_client.consultar_tramite(numero_tramite)

            if resultado and isinstance(resultado, list) and len(resultado) > 0:
                # La API devuelve un array, tomamos el primer elemento
                tramite_data = resultado[0]
                message = self._format_tramite_response(tramite_data, numero_tramite)
                dispatcher.utter_message(text=message)
            else:
                # Lista vacía o None
                self._handle_tramite_not_found(dispatcher, numero_tramite)

        except Exception as e:
            logger.error(f"Error en consulta API de trámite: {e}")
            self._handle_api_error(dispatcher, numero_tramite)

        return [SlotSet("ultimo_documento", numero_tramite)]

    def _format_tramite_response(self, data: Dict[str, Any], numero_tramite: str) -> str:
        """Formatea la respuesta de la API de trámites"""

        # Función helper para manejar valores que pueden ser None
        def safe_get_string(value):
            """Convierte None a string vacío, y aplica strip a strings"""
            if value is None:
                return ""
            return str(value).strip()

        # Extraer campos de la respuesta
        tramite_nro = safe_get_string(data.get('tramiteNro'))
        fecha_presentacion = safe_get_string(data.get('fechaPresentacion'))
        estado_desc = safe_get_string(data.get('estadoDesc'))
        resolucion_nro = safe_get_string(data.get('resolucionNro'))
        fecha_resolucion = safe_get_string(data.get('fechaResolucion'))
        resultado_des = safe_get_string(data.get('resultadoDes'))
        estado_notifica_res = safe_get_string(data.get('estadoNotificaRes'))
        fecha_notifica_res = safe_get_string(data.get('fechaNotificaRes'))

        # Verificar si el trámite existe
        if not tramite_nro and not estado_desc:
            return self._format_no_tramite_found(numero_tramite)

        # Formatear fechas usando la función del cliente SAT
        fecha_presentacion_fmt = sat_client.format_date(fecha_presentacion) if fecha_presentacion else "No disponible"
        fecha_resolucion_fmt = sat_client.format_date(fecha_resolucion) if fecha_resolucion else "No disponible"
        fecha_notifica_res_fmt = sat_client.format_date(fecha_notifica_res) if fecha_notifica_res else "No disponible"

        # Construir mensaje
        message = f"""📋 **INFORMACIÓN DEL TRÁMITE**

    📄 **Número de trámite:** {tramite_nro if tramite_nro else numero_tramite}
    📅 **Fecha de presentación:** {fecha_presentacion_fmt}
    📊 **Estado:** {estado_desc if estado_desc else 'No disponible'}
    """

        # Añadir N° de resolución solo si existe
        if resolucion_nro:
            message += f"📋 **N° de resolución:** {resolucion_nro}\n"

        # Añadir fecha de resolución solo si existe
        if fecha_resolucion_fmt and fecha_resolucion_fmt != "No disponible":
            message += f"📅 **Fecha de resolución:** {fecha_resolucion_fmt}\n"

        # Añadir resultado solo si existe
        if resultado_des:
            message += f"✅ **Resultado:** {resultado_des}\n"

        # Añadir estado de notificación solo si existe
        if estado_notifica_res:
            message += f"📬 **Estado de notificación:** {estado_notifica_res}\n"

        # Añadir fecha de notificación solo si existe
        if fecha_notifica_res_fmt and fecha_notifica_res_fmt != "No disponible":
            message += f"📅 **Fecha de notificación:** {fecha_notifica_res_fmt}\n"

        message += f"""
    **¿Qué más necesitas?**
    - 'Menú principal' - Otras opciones
    - 'Finalizar chat'
    """

        return message

    def _format_no_tramite_found(self, numero_tramite: str) -> str:
        """Formatea mensaje cuando no se encuentra el trámite"""

        message = f"""❌ **No se encontró información para el trámite {numero_tramite}**

🔍 **Posibles causas:**
• El número de trámite puede estar incorrecto
• El trámite aún no está registrado en el sistema

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        return message

    def _request_numero_tramite(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita número de trámite cuando no se proporcionó"""

        message = """Para consultar el estado de tu trámite necesito el número de trámite.

📋 **Formato requerido:**
• Exactamente **14 dígitos**
• Ejemplo: 12345678901234

**Ejemplos de cómo escribir:**
• "Mi trámite es 12345678901234"
• "Consultar trámite 98765432109876"

¿Cuál es tu número de trámite?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_numero(self, dispatcher: CollectingDispatcher,
                              numero: str) -> List[Dict[Text, Any]]:
        """Maneja números de trámite con formato inválido"""

        message = f"""❌ El número de trámite **{numero}** no tiene un formato válido.

📋 **Formato correcto:**
• Exactamente **14 dígitos**
• Solo números
• Ejemplo: 12345678901234

**El número que proporcionaste:**
• Longitud: {len(re.sub(r'[^0-9]', '', numero))} dígitos
• Se requieren exactamente 14 dígitos

Por favor, proporciona un número de trámite válido."""

        dispatcher.utter_message(text=message)
        return []

    def _handle_tramite_not_found(self, dispatcher: CollectingDispatcher, numero_tramite: str):
        """Maneja cuando el trámite no se encuentra en la base de datos"""
        message = self._format_no_tramite_found(numero_tramite)
        dispatcher.utter_message(text=message)

    def _handle_api_error(self, dispatcher: CollectingDispatcher, numero_tramite: str):
        """Maneja errores de la API"""

        message = f"""😔 Lo siento, tuve un problema técnico al consultar el trámite **{numero_tramite}**.

📱 **Mientras tanto puedes:**
• Consultar directamente en: https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx
• Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
• Intentar con otro número de trámite
• 'Otros trámites' - Ver opciones administrativas
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)