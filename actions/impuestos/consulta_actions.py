"""
Actions para consulta de impuestos
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from ..core.sat_api_client import sat_client


logger = logging.getLogger(__name__)


class DocumentProcessorImpuestos:
    """Procesador de documentos para consultas de impuestos"""

    @staticmethod
    def extract_document_from_message(tracker: Tracker) -> tuple[str, str]:
        """
        Extrae documento y tipo del mensaje del usuario

        Returns:
            tuple: (documento, tipo) donde tipo es 'placa', 'dni', 'ruc', 'codigo_contribuyente' o None
        """
        entities = tracker.latest_message.get('entities', [])
        intent = tracker.latest_message.get('intent', {}).get('name', '')

        # Buscar en entities
        for entity in entities:
            if entity['entity'] in ['placa', 'dni', 'ruc', 'codigo_contribuyente']:
                return entity['value'], entity['entity']

        # Inferir por intent
        if intent == 'consulta_rapida_impuestos_placa' or intent == 'impuestos_consultar_placa':
            texto = tracker.latest_message.get('text', '')
            placa_match = re.search(
                r'[A-Z]{2,3}[\s\-]*\d{3,4}|[A-Z][\s\-]*\d[\s\-]*[A-Z][\s\-]*\d{3}|U[\s\-]*\d[\s\-]*[A-Z][\s\-]*\d{3}',
                texto.upper())
            if placa_match:
                placa_limpia = re.sub(r'[\s\-]', '', placa_match.group())
                return placa_limpia, 'placa'

        elif intent == 'consulta_rapida_impuestos_dni' or intent == 'impuestos_consultar_dni':
            texto = tracker.latest_message.get('text', '')
            dni_match = re.search(r'(?<![A-Z0-9])\d{8}(?![A-Z0-9])', texto)
            if dni_match:
                return dni_match.group(), 'dni'

        elif intent == 'consulta_rapida_impuestos_ruc' or intent == 'impuestos_consultar_ruc':
            texto = tracker.latest_message.get('text', '')
            ruc_match = re.search(r'\b[12]\d{10}\b', texto)
            if ruc_match:
                return ruc_match.group(), 'ruc'

        elif intent == 'consulta_rapida_impuestos_codigo' or intent == 'impuestos_consultar_codigo':
            texto = tracker.latest_message.get('text', '')
            codigo_match = re.search(r'\b\d{1,10}\b', texto)
            if codigo_match:
                return codigo_match.group(), 'codigo_contribuyente'

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
            documento_limpio = re.sub(r'[^A-Z0-9]', '', documento_limpio)
            es_valido = len(documento_limpio) == 6 and documento_limpio.isalnum()
            return es_valido, documento_limpio

        elif tipo == 'dni':
            documento_limpio = re.sub(r'[^0-9]', '', documento_limpio)
            es_valido = len(documento_limpio) == 8 and documento_limpio.isdigit()
            return es_valido, documento_limpio

        elif tipo == 'ruc':
            documento_limpio = re.sub(r'[^0-9]', '', documento_limpio)
            es_valido = (len(documento_limpio) == 11 and
                         documento_limpio.isdigit() and
                         documento_limpio[0] in ['1', '2'])
            return es_valido, documento_limpio

        elif tipo == 'codigo_contribuyente':
            documento_limpio = re.sub(r'[^0-9]', '', documento_limpio)
            es_valido = (len(documento_limpio) >= 1 and
                         len(documento_limpio) <= 10 and
                         documento_limpio.isdigit())
            return es_valido, documento_limpio

        return False, ""


class ActionConsultarImpuestos(Action):
    """Action para consulta de impuestos y deuda tributaria"""

    def name(self) -> Text:
        return "action_consultar_impuestos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de impuestos")

        # 1. Extraer documento del mensaje
        documento, tipo = DocumentProcessorImpuestos.extract_document_from_message(tracker)

        if not documento or not tipo:
            return self._request_document(dispatcher)

        # 2. Validar formato
        es_valido, documento_limpio = DocumentProcessorImpuestos.validate_document(documento, tipo)

        if not es_valido:
            return self._handle_invalid_document(dispatcher, tipo, documento)

        # 3. Ejecutar consulta API
        logger.info(f"Consultando impuestos para {tipo}: {documento_limpio}")
        return self._execute_api_query(dispatcher, documento_limpio, tipo)

    def _execute_api_query(self, dispatcher: CollectingDispatcher,
                           documento: str, tipo: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API del SAT"""

        tipo_display = {
            'placa': 'PLACA',
            'dni': 'DNI',
            'ruc': 'RUC',
            'codigo_contribuyente': 'CÓDIGO DE CONTRIBUYENTE'
        }.get(tipo, tipo.upper())

        dispatcher.utter_message(text=f"🔍 Consultando para {tipo_display} **{documento}**...")

        try:
            # Llamar API según tipo
            if tipo == "codigo_contribuyente":
                resultado = sat_client.consultar_por_codigo_contribuyente(documento)
            elif tipo == "placa":
                resultado = sat_client.consultar_papeletas_por_placa(documento)
            elif tipo == "dni":
                resultado = sat_client.consultar_papeletas_por_dni(documento)
            elif tipo == "ruc":
                resultado = sat_client.consultar_papeletas_por_ruc(documento)
            else:
                return self._handle_api_error(dispatcher, tipo, documento)

            # Procesar resultado
            if resultado is not None:
                data_completa = resultado.get('data', [])

                # Ordenar poniendo impuestos primero
                data_ordenada = self._sort_results_impuestos_first(data_completa)

                message = self._format_impuestos_response(data_ordenada, tipo, documento)
                dispatcher.utter_message(text=message)
            else:
                self._handle_api_error(dispatcher, tipo, documento)

        except Exception as e:
            logger.error(f"Error en consulta API de impuestos: {e}")
            self._handle_api_error(dispatcher, tipo, documento)

        return [SlotSet("ultimo_documento", documento),
                SlotSet("fallback_count", 0)
                ]

    def _sort_results_impuestos_first(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ordena resultados poniendo impuestos/tributos primero, luego papeletas y otros

        Args:
            data: Lista de resultados de la API

        Returns:
            Lista ordenada
        """
        # Conceptos tributarios que van primero ()
        impuesto_conceptos = [
            'Imp. Predial',
            'Impuesto Predial',
            'Arbitrios',
            'Arbitrio',
            'Imp. Vehicular',
            'Impuesto Vehicular',
            'Alcabala',
            'Liquidacion Alcabala',
            'Mult. Tributaria',
            'Multas Tributarias'
        ]

        impuestos = []
        otros = []

        for item in data:
            concepto = item.get('concepto', '').strip()
            if any(imp in concepto for imp in impuesto_conceptos):
                impuestos.append(item)
            else:
                otros.append(item)

        # Impuestos primero, luego otros conceptos (papeletas, etc.)
        return impuestos + otros

    def _format_impuestos_response(self, data: List[Dict[str, Any]],
                                   tipo: str, documento: str) -> str:
        """
        Formatea la respuesta mostrando TODOS los conceptos con resumen por tipo

        Args:
            data: Lista COMPLETA de resultados (ya ordenada)
            tipo: Tipo de documento consultado
            documento: Número de documento

        Returns:
            Mensaje formateado
        """
        tipo_display = {
            'placa': 'PLACA',
            'dni': 'DNI',
            'ruc': 'RUC',
            'codigo_contribuyente': 'CÓDIGO DE CONTRIBUYENTE'
        }.get(tipo, tipo.upper())

        if not data:
            return f"""✅ **¡Excelente noticia!** No encontré deudas pendientes para {tipo_display} **{documento}**.

🎉 Estás al día.

**¿Qué más necesitas?**
- 'Menú principal' - Otras opciones
- 'Finalizar chat'

💡 **Tip:** Puedes declarar nuevos predios o vehículos en Agencia Virtual SAT."""

        cantidad_total = len(data)

        # CALCULAR MONTOS POR CONCEPTO
        montos_por_concepto = self._calcular_montos_por_concepto(data)
        total_general = sum(montos_por_concepto.values())

        # MOSTRAR HASTA 3 ITEMS DETALLADOS
        MAX_ITEMS = 3
        items_mostrar = data[:MAX_ITEMS]
        items_restantes = cantidad_total - MAX_ITEMS

        message = f"📋 **Encontré {cantidad_total} deuda{'s' if cantidad_total > 1 else ''} pendiente{'s' if cantidad_total > 1 else ''}** para {tipo_display} **{documento}**:\n\n"

        # Mostrar items detallados
        for i, item in enumerate(items_mostrar, 1):
            concepto = item.get('concepto', 'No especificado').strip()
            ano = item.get('ano', 'N/A').strip()
            cuota = item.get('cuota', '0').strip()
            monto = float(item.get('monto', 0))
            referencia = item.get('referencia', '').strip()
            estado = item.get('estado', '').strip()

            # Datos específicos de papeletas (si vienen mezcladas)
            falta = item.get('falta', '').strip()
            fecha_infraccion = item.get('fechainfraccion', '').strip()

            message += f"**💰 Deuda #{i}:**\n"
            message += f"• **Concepto:** {concepto}\n"

            # Año y Cuota en una sola línea
            if cuota and cuota != '0':
                message += f"• **Año - cuota:** {ano} - {cuota}\n"
            else:
                message += f"• **Año:** {ano}\n"

            if referencia:
                message += f"• **Referencia:** {referencia}\n"

            # Solo mostrar datos de papeletas si es una papeleta
            if concepto == 'Papeletas':
                if falta:
                    message += f"• **Tipo de falta:** {falta}\n"
                if fecha_infraccion:
                    message += f"• **Fecha infracción:** {fecha_infraccion}\n"

            message += f"• **Monto:** S/ {monto:,.2f}\n"

            if estado:
                message += f"• **Estado:** {estado}\n"

            message += "\n"

        # Indicar si hay más items
        if items_restantes > 0:
            message += f"... y {items_restantes} deuda{'s' if items_restantes > 1 else ''} más.\n\n"

        # RESUMEN POR CONCEPTO
        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💰 **RESUMEN POR CONCEPTO:**\n"
        for concepto, monto in sorted(montos_por_concepto.items()):
            message += f"• {concepto}: S/ {monto:,.2f}\n"

        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"💵 **TOTAL GENERAL:** S/ {total_general:,.2f}\n\n"

        # Mayor detalle cuando hay muchas deudas
        if cantidad_total > MAX_ITEMS:
            message += "📋 **MAYOR DETALLE EN EL SIGUIENTE LINK:**\n"
            message += "📌 https://www.sat.gob.pe/pagosenlinea/\n\n"

        # Recomendaciones según monto
        if total_general > 2000:
            message += "💡 **Recomendación:** El monto es considerable. Te sugiero ver la información sobre facilidades de pago.\n\n"

        # Opciones contextuales
        message += "**¿Qué más necesitas?**\n"
        message += "• 'Cómo pago' - Información para pagar\n"
        message += "• 'Facilidades' - Pagar en cuotas\n"
        message += "• 'Menú principal' - Otras opciones\n"
        message += "• 'Finalizar chat'\n"

        return message

    def _calcular_montos_por_concepto(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula el total por cada concepto

        Args:
            data: Lista completa de resultados

        Returns:
            Diccionario {concepto: monto_total}
        """
        montos = {}

        for item in data:
            concepto = item.get('concepto', 'Otros').strip()
            monto = float(item.get('monto', 0))

            if concepto in montos:
                montos[concepto] += monto
            else:
                montos[concepto] = monto

        return montos

    def _request_document(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita documento cuando no se proporcionó información"""

        message = """Para consultar deuda tributaria necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, APS583, U1A710
🆔 **Tu DNI** - 8 dígitos (ej: 12345678)
🏢 **RUC** - 11 dígitos (ej: 20123456789)
🏠 **Código de contribuyente** - Ej: 94539

**Ejemplos de cómo escribir:**
• "Impuestos de mi placa APS583"
• "Deuda tributaria DNI 87654321"

¿Cuál puedes proporcionar?"""

        dispatcher.utter_message(text=message)
        return []

    def _handle_invalid_document(self, dispatcher: CollectingDispatcher,
                                 tipo: str, documento: str) -> List[Dict[Text, Any]]:
        """Maneja documentos con formato inválido"""

        error_messages = {
            'placa': f"""❌ La placa **{documento}** no tiene un formato válido.

**Formatos correctos:**
• ABC123
• U1A710
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

Por favor, proporciona un RUC válido.""",

            'codigo_contribuyente': f"""❌ El código de contribuyente **{documento}** no es válido.

**Formato correcto:**
• Solo números


Por favor, proporciona un código válido."""
        }

        message = error_messages.get(tipo, f"❌ El dato **{documento}** no es válido.")
        dispatcher.utter_message(text=message)
        return []

    def _handle_api_error(self, dispatcher: CollectingDispatcher,
                          tipo: str, documento: str):
        """Maneja errores de la API"""

        tipo_display = {
            'placa': 'PLACA',
            'dni': 'DNI',
            'ruc': 'RUC',
            'codigo_contribuyente': 'CÓDIGO DE CONTRIBUYENTE'
        }.get(tipo, tipo.upper())

        message = f"""😔 Lo siento, tuve un problema técnico al consultar {tipo_display} **{documento}**.

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