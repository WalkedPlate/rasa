"""
Router inteligente para disambiguar entre papeletas e impuestos
"""
from typing import Any, Text, Dict, List, Optional, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import logging

logger = logging.getLogger(__name__)


class ActionRouteDocumentConsultation(Action):
    """Router que decide entre papeletas e impuestos basado en contexto"""

    def name(self) -> Text:
        return "action_route_document_consultation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando router para consulta de documentos")

        # Verificar si hay clarificación pendiente
        esperando_clarificacion = tracker.get_slot("esperando_clarificacion")
        if esperando_clarificacion:
            return self._process_clarification(dispatcher, tracker)

        # Extraer documento y tipo
        documento, tipo_doc = self._extract_document_data(tracker)

        if not documento or not tipo_doc:
            logger.warning("No se pudo extraer documento del mensaje")
            return self._request_document(dispatcher)

        # Determinar contexto inteligentemente
        context = self._determine_context_intelligently(tracker)

        logger.info(f"Contexto determinado: {context} para {tipo_doc} {documento}")

        if context == "papeletas":
            return self._route_to_papeletas(tracker, documento, tipo_doc)
        elif context == "impuestos":
            return self._route_to_impuestos(tracker, documento, tipo_doc)
        else:
            return self._ask_clarification(dispatcher, documento, tipo_doc)

    def _extract_document_data(self, tracker: Tracker) -> Tuple[Optional[str], Optional[str]]:
        """Extrae documento y tipo del mensaje actual"""

        entities = tracker.latest_message.get('entities', [])

        for entity in entities:
            entity_type = entity['entity']
            if entity_type in ['placa', 'dni', 'ruc', 'codigo_contribuyente']:
                return entity['value'], entity_type

        # Verificar slots si no hay entities
        documento = tracker.get_slot("documento_pendiente")
        tipo_doc = tracker.get_slot("tipo_documento_pendiente")

        if documento and tipo_doc:
            return documento, tipo_doc

        return None, None

    def _determine_context_intelligently(self, tracker: Tracker) -> str:
        """Determina contexto usando múltiples heurísticas"""

        # 1. Verificar contexto actual explícito
        current_context = tracker.get_slot("contexto_actual")
        if current_context in ["papeletas", "impuestos", "retencion"]:
            logger.debug(f"Contexto explícito encontrado: {current_context}")
            return current_context

        # 2. FORZAR ambigüedad para documentos sin contexto explícito
        current_intent = tracker.latest_message.get('intent', {}).get('name', '')
        if current_intent == 'consulta_ambigua_documento':
            logger.debug("Documento ambiguo detectado - forzando clarificación")
            return "ambiguous"

        # 3. Analizar palabras clave en el mensaje actual
        text = tracker.latest_message.get('text', '').lower()

        # Palabras clave para papeletas
        papeletas_keywords = [
            'papeleta', 'multa', 'infraccion', 'codigo', 'falta',
            'transito', 'manejar', 'conductor'
        ]

        # Palabras clave para impuestos
        impuestos_keywords = [
            'impuesto', 'predial', 'vehicular', 'arbitrio', 'tributario',
            'contribuyente', 'deuda', 'tributo', 'alcabala'
        ]

        papeletas_score = sum(1 for word in papeletas_keywords if word in text)
        impuestos_score = sum(1 for word in impuestos_keywords if word in text)

        if papeletas_score > impuestos_score and papeletas_score > 0:
            logger.debug(f"Contexto por palabras clave: papeletas (score: {papeletas_score})")
            return "papeletas"
        elif impuestos_score > papeletas_score and impuestos_score > 0:
            logger.debug(f"Contexto por palabras clave: impuestos (score: {impuestos_score})")
            return "impuestos"

        # 4. Analizar historial reciente de conversación
        recent_context = self._analyze_conversation_history(tracker)
        if recent_context:
            logger.debug(f"Contexto por historial: {recent_context}")
            return recent_context

        # 5. Verificar intent específico
        intent = tracker.latest_message.get('intent', {}).get('name', '')

        if any(keyword in intent for keyword in ['papeletas', 'codigo_falta']):
            return "papeletas"
        elif any(keyword in intent for keyword in ['impuestos', 'tributario', 'contribuyente']):
            return "impuestos"

        # 6. Si no hay contexto claro, SIEMPRE es ambiguo
        logger.debug("No se pudo determinar contexto - forzando clarificación")
        return "ambiguous"

    def _analyze_conversation_history(self, tracker: Tracker) -> Optional[str]:
        """Analiza historial reciente para inferir contexto"""

        events = tracker.events[-10:]  # Últimos 10 eventos

        for event in reversed(events):
            if event.get('event') == 'user':
                intent = event.get('parse_data', {}).get('intent', {}).get('name', '')

                if any(keyword in intent for keyword in ['papeletas', 'codigo_falta']):
                    return "papeletas"
                elif any(keyword in intent for keyword in ['impuestos', 'tributario', 'contribuyente']):
                    return "impuestos"

            elif event.get('event') == 'action':
                action_name = event.get('name', '')

                if 'papeletas' in action_name:
                    return "papeletas"
                elif 'impuestos' in action_name:
                    return "impuestos"

        return None

    def _route_to_papeletas(self, tracker: Tracker, documento: str, tipo_doc: str) -> List[Dict[Text, Any]]:
        """Rutea a action de papeletas existente"""

        logger.info(f"Ruteando a papeletas: {tipo_doc} {documento}")

        return [
            SlotSet("documento_consulta", documento),
            SlotSet("tipo_documento", tipo_doc),
            SlotSet("contexto_actual", "papeletas"),
            SlotSet("esperando_clarificacion", False),
            FollowupAction("action_consultar_papeletas")
        ]

    def _route_to_impuestos(self, tracker: Tracker, documento: str, tipo_doc: str) -> List[Dict[Text, Any]]:
        """Rutea a action de impuestos nuevo"""

        logger.info(f"Ruteando a impuestos: {tipo_doc} {documento}")

        return [
            SlotSet("documento_consulta", documento),
            SlotSet("tipo_documento", tipo_doc),
            SlotSet("contexto_actual", "impuestos"),
            SlotSet("esperando_clarificacion", False),
            FollowupAction("action_consultar_impuestos")
        ]

    def _ask_clarification(self, dispatcher: CollectingDispatcher,
                           documento: str, tipo_doc: str) -> List[Dict[Text, Any]]:
        """Solicita clarificación cuando el contexto es ambiguo"""

        logger.info(f"Solicitando clarificación para: {tipo_doc} {documento}")

        doc_display = {
            'placa': 'PLACA',
            'dni': 'DNI',
            'ruc': 'RUC',
            'codigo_contribuyente': 'CÓDIGO DE CONTRIBUYENTE'
        }.get(tipo_doc, tipo_doc.upper())

        message = f"""Para el {doc_display} **{documento}**, ¿qué información necesitas?

🚗 **Papeletas e infracciones** - Multas de tránsito
💰 **Impuestos** - Deuda tributaria (predial, vehicular, arbitrios)

Responde:
• "papeletas" o "infracciones" o "multas"
• "impuestos" o "deuda tributaria" o "tributos"""

        dispatcher.utter_message(text=message)

        return [
            SlotSet("documento_pendiente", documento),
            SlotSet("tipo_documento_pendiente", tipo_doc),
            SlotSet("esperando_clarificacion", True)
        ]

    def _process_clarification(self, dispatcher: CollectingDispatcher,
                               tracker: Tracker) -> List[Dict[Text, Any]]:
        """Procesa la clarificación del usuario"""

        intent = tracker.latest_message['intent']['name']
        documento = tracker.get_slot("documento_pendiente")
        tipo_doc = tracker.get_slot("tipo_documento_pendiente")

        if not documento or not tipo_doc:
            logger.warning("No hay documento pendiente para clarificar")
            return [SlotSet("esperando_clarificacion", False)]

        # Analizar respuesta del usuario
        text = tracker.latest_message.get('text', '').lower()

        # Palabras que indican papeletas
        if any(word in text for word in ['papeleta', 'multa', 'infraccion', 'transito']):
            logger.info(f"Clarificación recibida: papeletas para {tipo_doc} {documento}")
            return self._route_to_papeletas(tracker, documento, tipo_doc)

        # Palabras que indican impuestos
        elif any(word in text for word in ['impuesto', 'tributario', 'deuda', 'tributo', 'predial', 'vehicular']):
            logger.info(f"Clarificación recibida: impuestos para {tipo_doc} {documento}")
            return self._route_to_impuestos(tracker, documento, tipo_doc)

        # Intent específicos
        elif intent == "clarify_papeletas":
            return self._route_to_papeletas(tracker, documento, tipo_doc)
        elif intent == "clarify_impuestos":
            return self._route_to_impuestos(tracker, documento, tipo_doc)

        else:
            # Usuario no respondió claramente, pedir de nuevo
            doc_display = tipo_doc.upper().replace('_', ' ')
            message = f"Para el {doc_display} **{documento}**, por favor especifica:\n\n• 'papeletas' para infracciones de tránsito\n• 'impuestos' para deuda tributaria"
            dispatcher.utter_message(text=message)
            return []

    def _request_document(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita documento cuando no se proporcionó"""

        message = """Para consultar necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, APS583, U1A710
🆔 **Tu DNI** - 8 dígitos (ej: 12345678)
🏢 **RUC** - 11 dígitos (ej: 20123456789)
🏠 **Código de contribuyente** - Ej: 94539

**¿Qué quieres consultar?**
• "Papeletas de mi placa ABC123"
• "Impuestos de mi DNI 12345678"

¿Cuál puedes proporcionar?"""

        dispatcher.utter_message(text=message)
        return []