"""
Actions para consulta de códigos de falta con API del SAT
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

from ..core.validators import validator
from ..core.sat_api_client import sat_client

logger = logging.getLogger(__name__)

class ActionConsultarCodigoFalta(Action):
    """Action inteligente que maneja todo el flujo de consulta de códigos de falta"""

    def name(self) -> Text:
        return "action_consultar_codigo_falta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("🔢 Iniciando consulta de código de falta")

        # Estado actual
        esperando_confirmacion = tracker.get_slot("esperando_confirmacion") or False

        if esperando_confirmacion:
            return self._procesar_confirmacion(dispatcher, tracker)
        else:
            return self._iniciar_consulta(dispatcher, tracker)

    def _iniciar_consulta(self, dispatcher: CollectingDispatcher,
                         tracker: Tracker) -> List[Dict[Text, Any]]:
        """Inicia el proceso de consulta detectando código disponible"""

        # Obtener código de slot y entities
        codigo_falta = tracker.get_slot("codigo_falta")

        # También revisar entities del último mensaje
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity['entity'] == 'codigo_falta' and not codigo_falta:
                codigo_falta = entity['value']

        logger.info(f"📊 Código detectado: {codigo_falta}")

        if codigo_falta:
            return self._procesar_codigo(dispatcher, codigo_falta)
        else:
            return self._solicitar_codigo(dispatcher)

    def _procesar_codigo(self, dispatcher: CollectingDispatcher,
                        codigo: str) -> List[Dict[Text, Any]]:
        """Procesa y valida el código de falta"""

        # Validar formato
        es_valido, codigo_limpio = validator.validate_codigo_falta(codigo)

        if not es_valido:
            mensaje = validator.get_validation_message('codigo_falta', False, codigo)
            dispatcher.utter_message(text=mensaje)
            return [SlotSet("codigo_falta", None)]

        # Pedir confirmación
        mensaje = f"Detecté el código de falta **{codigo_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=mensaje)

        return [
            SlotSet("codigo_falta", codigo_limpio),
            SlotSet("dato_detectado", "codigo_falta"),
            SlotSet("esperando_confirmacion", True)
        ]

    def _solicitar_codigo(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita código cuando no se proporcionó"""

        mensaje = """Estimado ciudadano, indique el **CÓDIGO DE FALTA**:

📝 **Ejemplos de códigos:**
• C15, M08, A05, T12
• G25, F03, B20, L18

¿Cuál es el código que quieres consultar?"""

        dispatcher.utter_message(text=mensaje)
        return []

    def _procesar_confirmacion(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker) -> List[Dict[Text, Any]]:
        """Procesa la confirmación del usuario"""

        intent = tracker.latest_message['intent']['name']
        dato_detectado = tracker.get_slot("dato_detectado")

        logger.info(f"🔄 Procesando confirmación - Intent: {intent}, Dato: {dato_detectado}")

        if intent == "confirm_yes":
            return self._ejecutar_consulta_api(dispatcher, tracker)

        elif intent == "confirm_no":
            return self._manejar_correccion(dispatcher)

        else:
            # Intent no reconocido durante confirmación
            codigo = tracker.get_slot("codigo_falta")
            mensaje = f"Para el código **{codigo}**, necesito que confirmes:\n\n✅ Di 'sí' si es correcto\n❌ Di 'no' si necesitas corregirlo"
            dispatcher.utter_message(text=mensaje)
            return []

    def _ejecutar_consulta_api(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker) -> List[Dict[Text, Any]]:
        """Ejecuta la consulta a la API de códigos de falta"""

        codigo = tracker.get_slot("codigo_falta")

        dispatcher.utter_message(text=f"🔍 Consultando información del código **{codigo}**...")

        # Consultar API
        resultado = sat_client.consultar_codigo_falta(codigo)

        # Procesar resultado
        if resultado is not None:
            # Verificar si la respuesta tiene datos
            if isinstance(resultado, list) and len(resultado) > 0:
                mensaje = self._formatear_respuesta_codigo(resultado, codigo)
                dispatcher.utter_message(text=mensaje)
            elif isinstance(resultado, dict) and resultado:
                mensaje = self._formatear_respuesta_codigo(resultado, codigo)
                dispatcher.utter_message(text=mensaje)
            else:
                # Respuesta vacía - código no encontrado
                self._manejar_codigo_no_encontrado(dispatcher, codigo)
        else:
            self._manejar_error_api(dispatcher, codigo)

        return self._reset_slots()

    def _manejar_codigo_no_encontrado(self, dispatcher: CollectingDispatcher, codigo: str):
        """Maneja cuando el código no se encuentra en la base de datos"""

        mensaje = f"""❌ El código **{codigo}** no se encontró en la base de datos del SAT.

🔍 **Posibles causas:**
• El código puede estar mal escrito
• Podría ser un código desactualizado
• Puede que no exista ese código específico

💡 **Sugerencias:**
• Verifica que el código esté correctamente escrito
• Consulta directamente en: https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx
• Si tienes una papeleta física, verifica el código en el documento

¿Quieres intentar con otro código?"""

        dispatcher.utter_message(text=mensaje)

    def _formatear_respuesta_codigo(self, data: Dict[str, Any], codigo: str) -> str:
        """Formatea la respuesta de la API de códigos de falta"""

        # Extraer datos de la respuesta
        codigo_falta = data.get('codigo', codigo)
        infraccion = data.get('infraccion', 'No disponible')
        calificacion = data.get('calificacion', 'No disponible')
        porcentaje_uit = data.get('porcentaje_uit', 'No disponible')
        monto = data.get('monto', 'No disponible')
        sancion = data.get('sancion', 'No disponible')
        puntos = data.get('puntos', 'No disponible')
        medida_preventiva = data.get('medida_preventiva', 'No disponible')

        # Formatear respuesta según el formato original del SAT
        mensaje = f"""La falta corresponde a:

**CÓDIGO FALTA:** {codigo_falta}
**INFRACCIÓN:** {infraccion}
**CALIFICACIÓN:** {calificacion}
**%UIT:** {porcentaje_uit}
**MONTO:** S/ {monto}
**SANCIÓN:** {sancion}
**PUNTOS:** {puntos}
**MEDIDA PREVENTIVA:** {medida_preventiva}

MAYOR DETALLE EN EL SIGUIENTE LINK:
📌https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx"""

        return mensaje

    def _manejar_error_api(self, dispatcher: CollectingDispatcher, codigo: str):
        """Maneja errores de la API de forma amigable"""

        mensaje = f"""😔 Lo siento, tuve un problema técnico al consultar el código **{codigo}**.

🔧 Esto puede ocurrir por:
• Mantenimiento del sistema del SAT
• El código no existe en la base de datos
• Problemas temporales de conexión

📱 **Mientras tanto, puedes:**
• Consultar directamente en: https://www.sat.gob.pe/WebSiteV8/Modulos/contenidos/mult_Papeletas_ti_rntv2.aspx
• Verificar que el código esté bien escrito
• Intentar nuevamente en unos minutos

⏰ ¿Quieres intentar con otro código o necesitas ayuda con algo más?"""

        dispatcher.utter_message(text=mensaje)

    def _manejar_correccion(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Maneja cuando el usuario indica que el código es incorrecto"""

        mensaje = """¿Cuál es el código correcto?

📝 **Recuerda el formato:**
• C15, M08, A05 (letra + números)
• T12, G25, F03, etc.

Por favor, proporciona el código correcto:"""

        dispatcher.utter_message(text=mensaje)

        return [
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("codigo_falta", None)
        ]

    def _reset_slots(self) -> List[Dict[Text, Any]]:
        """Resetea slots después de completar consulta"""
        return [
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("tipo_consulta_actual", None)
        ]