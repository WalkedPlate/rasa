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
    """Router que decide entre papeletas e impuestos sin modificar actions existentes"""

    def name(self) -> Text:
        return "action_route_document_consultation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando router de consulta de documentos")

        # Verificar si hay clarificación pendiente
        esperando_clarificacion = tracker.get_slot("esperando_clarificacion")
        if esperando_clarificacion:
            return self._process_clarification(dispatcher, tracker)

        # Extraer documento y tipo
        documento, tipo_doc = self._extract_document_data(tracker)

        if not documento or not tipo_doc:
            logger.warning("No se pudo extraer documento del mensaje")
            return []

        # Determinar contexto
        context = self._determine_context_safely(tracker)

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

    def _determine_context_safely(self, tracker: Tracker) -> str:
        """Determina contexto sin interferir con lógica existente"""

        # 1. Verificar slot de contexto actual
        current_context = tracker.get_slot("contexto_actual")
        if current_context in ["papeletas", "impuestos"]:
            return current_context

        # 2. Buscar en historial reciente (últimos 6 eventos de usuario)
        user_events = [e for e in tracker.events[-12:] if e.get('event') == 'user']

        for event in reversed(user_events[-6:]):
            intent_name = event.get('parse_data', {}).get('intent', {}).get('name', '')

            # Palabras clave para papeletas
            papeletas_keywords = ['papeletas', 'multa', 'infraccion', 'codigo_falta', 'falta']
            if any(keyword in intent_name.lower() for keyword in papeletas_keywords):
                return "papeletas"

            # Palabras clave para impuestos
            impuestos_keywords = ['impuestos', 'tributario', 'vehicular', 'predial', 'contribuyente']
            if any(keyword in intent_name.lower() for keyword in impuestos_keywords):
                return "impuestos"

        # 3. Si no hay contexto claro, es ambiguo
        return "ambiguous"

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

        doc_display = tipo_doc.upper().replace('_', ' ')

        message = f"""Para el {doc_display} **{documento}**, ¿qué información necesitas?

🚗 **Papeletas e infracciones** - Multas de tránsito
💰 **Impuestos** - Deuda tributaria

Responde algo como:
• "papeletas" o "infracciones"  
• "impuestos" o "deuda tributaria" """

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

        if intent == "clarify_papeletas":
            logger.info(f"Clarificación recibida: papeletas para {tipo_doc} {documento}")
            return self._route_to_papeletas(tracker, documento, tipo_doc)
        elif intent == "clarify_impuestos":
            logger.info(f"Clarificación recibida: impuestos para {tipo_doc} {documento}")
            return self._route_to_impuestos(tracker, documento, tipo_doc)
        else:
            # Usuario no respondió claramente, pedir de nuevo
            doc_display = tipo_doc.upper().replace('_', ' ')
            message = f"Para el {doc_display} **{documento}**, por favor especifica:\n\n• 'papeletas' para infracciones de tránsito\n• 'impuestos' para deuda tributaria"
            dispatcher.utter_message(text=message)
            return []