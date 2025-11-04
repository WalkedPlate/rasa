"""
Actions para consulta de impuestos
"""
from typing import Any, Text, Dict, List,  Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from actions.api.sat_client import sat_client
from actions.api.backend_client import backend_client

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
        logger.info(f"Consultando deudas para {tipo}: {documento_limpio}")
        return self._execute_api_query(dispatcher, tracker, documento_limpio, tipo)

    def _execute_api_query(self, dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           documento: str, tipo: str) -> List[Dict[Text, Any]]:
        """Ejecuta consulta a la API del SAT"""

        tipo_display = {
            'placa': 'PLACA',
            'dni': 'DNI',
            'ruc': 'RUC',
            'codigo_contribuyente': 'CÓDIGO DE CONTRIBUYENTE'
        }.get(tipo, tipo.upper())

        dispatcher.utter_message(text=f"🔍 Consultando deudas para {tipo_display} **{documento}**...")

        try:
            # Mapeo de tipo a query_type y document_type
            query_type_map = {
                'codigo_contribuyente': 'taxes_by_taxpayer_code',
                'placa': 'taxes_by_plate',
                'dni': 'taxes_by_dni',
                'ruc': 'taxes_by_ruc'
            }

            document_type_map = {
                'codigo_contribuyente': 'taxpayer_code',
                'placa': 'plate',
                'dni': 'dni',
                'ruc': 'ruc'
            }

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

            # Registrar consulta de la conversación en el backend (no bloqueante)
            try:
                backend_client.log_bot_query(
                    phone_number=tracker.sender_id,
                    query_type=query_type_map.get(tipo, tipo),
                    document_type=document_type_map.get(tipo, tipo),
                    document_value=documento
                )
            except Exception as e:
                logger.warning(f"No se pudo registrar consulta en backend: {e}")

            # Procesar resultado de la API del SAT
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
        Formatea la respuesta agrupando por concepto+año y mostrando cuota 0 como encabezado

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
            return f"""✅ **¡Excelente noticia!** No encontré deudas para {tipo_display} **{documento}**.

    🎉 Estás al día.

    **¿Qué más necesitas?**
    - 'Menú principal' - Otras opciones
    - 'Finalizar chat'

    💡 **Tip:** Puedes declarar nuevos predios o vehículos en Agencia Virtual SAT."""

        # Agrupar por concepto + año
        grupos = self._agrupar_por_concepto_ano(data)

        # Calcular solo cuotas individuales para el total
        total_general = sum(
            float(item.get('monto', 0))
            for item in data
            if item.get('cuota', '0').strip() != '0'
        )

        # Calcular resumen por concepto (solo cuotas individuales)
        montos_por_concepto = self._calcular_montos_por_concepto_sin_cuota_cero(data)

        message = f"📋 **Encontré deudas pendientes** para {tipo_display} **{documento}**:\n\n"

        # Mostrar cada grupo
        mostrados = 0
        limite_detalles = 2  # Solo mostrar detalle de los primeros 2 años

        for grupo_key, grupo_data in grupos.items():
            concepto, ano = grupo_key

            # Buscar registro con cuota 0 (resumen del año)
            cuota_cero = next((item for item in grupo_data if item.get('cuota', '0').strip() == '0'), None)

            # Filtrar cuotas individuales
            cuotas_individuales = [item for item in grupo_data if item.get('cuota', '0').strip() != '0']

            if not cuota_cero and not cuotas_individuales:
                continue

            # Calcular monto del año
            monto_ano = float(cuota_cero.get('monto', 0)) if cuota_cero else sum(
                float(c.get('monto', 0)) for c in cuotas_individuales)

            message += f"💰 **{concepto} {ano} - Total año:** S/ {monto_ano:,.2f}\n"

            # Solo mostrar detalle del primer año
            if mostrados < limite_detalles:
                # Mostrar cuota 0 si existe
                if cuota_cero:
                    message += f"   • **Año-cuota:** {ano}-0\n"
                    documento_pago = cuota_cero.get('documento', '').strip()
                    if documento_pago:
                        message += f"   • **Doc. de pago:** {documento_pago}\n"
                    message += f"   • **Monto:** S/ {float(cuota_cero.get('monto', 0)):,.2f}\n\n"

                # Mostrar referencia una sola vez
                referencia_item = cuotas_individuales[0] if cuotas_individuales else cuota_cero
                if referencia_item:
                    referencia = referencia_item.get('referencia', '').strip()
                    if referencia:
                        message += f"   **Referencia:** {referencia}\n\n"

                # Mostrar cuotas individuales
                for item in cuotas_individuales:
                    cuota = item.get('cuota', '0').strip()
                    monto = float(item.get('monto', 0))
                    documento_pago = item.get('documento', '').strip()
                    fecha_venc = item.get('fechavencimiento', '').strip()
                    estado = item.get('estado', '').strip()

                    message += f"   • **Año-cuota:** {ano}-{cuota}\n"

                    if documento_pago:
                        message += f"   • **Doc. de pago:** {documento_pago}\n"

                    # Solo para papeletas: añadir estos campos adicionales

                    if fecha_venc:
                        message += f"   • **Fecha vencimiento:** {fecha_venc}\n"

                    if estado:
                        message += f"   • **Estado:** {estado}\n"

                    message += f"   • **Monto:** S/ {monto:,.2f}\n\n"

                mostrados += 1

            message += "\n"

        # Si hay más años, indicar al usuario
        if len(grupos) > limite_detalles:
            message += "📌 **Para ver el detalle completo de todos los años, ingresa a:**\n"
            message += "https://www.sat.gob.pe/PagosEnlinea/\n\n"

        # RESUMEN POR CONCEPTO
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💰 **RESUMEN POR CONCEPTO:**\n"
        for concepto, monto in sorted(montos_por_concepto.items()):
            message += f"• {concepto}: S/ {monto:,.2f}\n"

        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"💵 **TOTAL GENERAL:** S/ {total_general:,.2f}\n\n"

        # Recomendaciones según monto
        if total_general > 2000:
            message += "💡 **Recomendación:** El monto es considerable. Te sugiero ver la información sobre facilidades de pago.\n\n"

        # Opciones contextuales
        message += "**¿Qué más necesitas?**\n"
        message += "• 'Cómo pago' - Información para pagar\n"
        message += "• 'Menú principal' - Otras opciones\n"
        message += "• 'Finalizar chat'\n"

        return message

    def _agrupar_por_concepto_ano(self, data: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
        """
        Agrupa los resultados por concepto y año

        Args:
            data: Lista completa de resultados

        Returns:
            Diccionario con clave (concepto, año) y valor lista de registros
        """
        grupos = {}

        for item in data:
            concepto = item.get('concepto', 'Otros').strip()
            ano = item.get('ano', 'N/A').strip()

            clave = (concepto, ano)

            if clave not in grupos:
                grupos[clave] = []

            grupos[clave].append(item)

        return grupos

    def _calcular_montos_por_concepto_sin_cuota_cero(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula el total por cada concepto excluyendo registros con cuota 0

        Args:
            data: Lista completa de resultados

        Returns:
            Diccionario {concepto: monto_total}
        """
        montos = {}

        for item in data:
            # Ignorar registros con cuota 0
            cuota = item.get('cuota', '0').strip()
            if cuota == '0':
                continue

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
• "Deudas de la placa ABC123"
• "Deudas del DNI 87654321"
• "Deudas del RUC 20123456789"

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

📱 **Mientras tanto puedes:**
• Consultar directamente en: https://www.sat.gob.pe/pagosenlinea/
• Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
• Intentar con otro documento
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)