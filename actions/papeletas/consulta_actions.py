"""
Actions para consulta de papeletas con APIs del SAT
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

from ..core.validators import validator
from ..core.sat_api_client import sat_client

logger = logging.getLogger(__name__)


class ActionConsultarPapeletas(Action):
    """Action inteligente que maneja todo el flujo de consulta de papeletas"""

    def name(self) -> Text:
        return "action_consultar_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("🚗 Iniciando consulta de papeletas")

        # Estado actual
        esperando_confirmacion = tracker.get_slot("esperando_confirmacion") or False

        if esperando_confirmacion:
            return self._procesar_confirmacion(dispatcher, tracker)
        else:
            return self._iniciar_consulta(dispatcher, tracker)

    def _iniciar_consulta(self, dispatcher: CollectingDispatcher,
                          tracker: Tracker) -> List[Dict[Text, Any]]:
        """Inicia el proceso de consulta detectando datos disponibles"""

        # Obtener datos de slots y entities
        placa = tracker.get_slot("placa")
        dni = tracker.get_slot("dni")
        ruc = tracker.get_slot("ruc")

        # También revisar entities del último mensaje
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity['entity'] == 'placa' and not placa:
                placa = entity['value']
            elif entity['entity'] == 'dni' and not dni:
                dni = entity['value']
            elif entity['entity'] == 'ruc' and not ruc:
                ruc = entity['value']

        logger.info(f"📊 Datos detectados - Placa: {placa}, DNI: {dni}, RUC: {ruc}")

        # Determinar qué dato usar (prioridad: placa > dni > ruc)
        if placa:
            return self._procesar_placa(dispatcher, placa)
        elif dni:
            return self._procesar_dni(dispatcher, dni)
        elif ruc:
            return self._procesar_ruc(dispatcher, ruc)
        else:
            return self._solicitar_datos(dispatcher)

    def _procesar_placa(self, dispatcher: CollectingDispatcher,
                        placa: str) -> List[Dict[Text, Any]]:
        """Procesa consulta por placa"""

        # Validar formato
        es_valida, placa_limpia = validator.validate_placa(placa)

        if not es_valida:
            mensaje = validator.get_validation_message('placa', False, placa)
            dispatcher.utter_message(text=mensaje)
            return [SlotSet("placa", None)]

        # Pedir confirmación
        mensaje = f"Detecté la placa **{placa_limpia}**. ¿Es correcta?"
        dispatcher.utter_message(text=mensaje)

        return [
            SlotSet("placa", placa_limpia),
            SlotSet("dato_detectado", "placa"),
            SlotSet("esperando_confirmacion", True)
        ]

    def _procesar_dni(self, dispatcher: CollectingDispatcher,
                      dni: str) -> List[Dict[Text, Any]]:
        """Procesa consulta por DNI"""

        # Validar formato
        es_valido, dni_limpio = validator.validate_dni(dni)

        if not es_valido:
            mensaje = validator.get_validation_message('dni', False, dni)
            dispatcher.utter_message(text=mensaje)
            return [SlotSet("dni", None)]

        # Pedir confirmación
        mensaje = f"Detecté el DNI **{dni_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=mensaje)

        return [
            SlotSet("dni", dni_limpio),
            SlotSet("dato_detectado", "dni"),
            SlotSet("esperando_confirmacion", True)
        ]

    def _procesar_ruc(self, dispatcher: CollectingDispatcher,
                      ruc: str) -> List[Dict[Text, Any]]:
        """Procesa consulta por RUC"""

        # Validar formato
        es_valido, ruc_limpio = validator.validate_ruc(ruc)

        if not es_valido:
            mensaje = validator.get_validation_message('ruc', False, ruc)
            dispatcher.utter_message(text=mensaje)
            return [SlotSet("ruc", None)]

        # Pedir confirmación
        mensaje = f"Detecté el RUC **{ruc_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=mensaje)

        return [
            SlotSet("ruc", ruc_limpio),
            SlotSet("dato_detectado", "ruc"),
            SlotSet("esperando_confirmacion", True)
        ]

    def _solicitar_datos(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Solicita datos cuando no se proporcionaron"""

        mensaje = """Para consultar tus papeletas necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, U1A710
🆔 **Tu DNI** - 8 dígitos
🏢 **RUC** - 11 dígitos

¿Cuál prefieres proporcionar?"""

        dispatcher.utter_message(text=mensaje)
        return []

    def _procesar_confirmacion(self, dispatcher: CollectingDispatcher,
                               tracker: Tracker) -> List[Dict[Text, Any]]:
        """Procesa la confirmación del usuario"""

        intent = tracker.latest_message['intent']['name']
        dato_detectado = tracker.get_slot("dato_detectado")

        logger.info(f"🔄 Procesando confirmación - Intent: {intent}, Dato: {dato_detectado}")

        if intent == "confirm_yes":
            return self._ejecutar_consulta_api(dispatcher, tracker, dato_detectado)

        elif intent == "confirm_no":
            return self._manejar_correccion(dispatcher, dato_detectado)

        else:
            # Intent no reconocido durante confirmación
            mensaje = f"Por favor, confirma si el {dato_detectado} es correcto:\n\n✅ Di 'sí' si es correcto\n❌ Di 'no' si necesitas corregirlo"
            dispatcher.utter_message(text=mensaje)
            return []

    def _ejecutar_consulta_api(self, dispatcher: CollectingDispatcher,
                               tracker: Tracker, dato_tipo: str) -> List[Dict[Text, Any]]:
        """Ejecuta la consulta a la API correspondiente"""

        if dato_tipo == "placa":
            placa = tracker.get_slot("placa")
            dispatcher.utter_message(text=f"🔍 Consultando papeletas para la placa **{placa}**...")
            resultado = sat_client.consultar_papeletas_por_placa(placa)

        elif dato_tipo == "dni":
            dni = tracker.get_slot("dni")
            dispatcher.utter_message(text=f"🔍 Consultando papeletas asociadas al DNI **{dni}**...")
            resultado = sat_client.consultar_papeletas_por_dni(dni)

        elif dato_tipo == "ruc":
            ruc = tracker.get_slot("ruc")
            dispatcher.utter_message(text=f"🔍 Consultando papeletas para el RUC **{ruc}**...")
            resultado = sat_client.consultar_papeletas_por_ruc(ruc)

        else:
            dispatcher.utter_message(text="❌ Error interno: tipo de dato no reconocido")
            return self._reset_slots()

        # Procesar resultado
        if resultado is not None:
            mensaje = self._formatear_respuesta_papeletas(resultado, dato_tipo, tracker)
            dispatcher.utter_message(text=mensaje)
        else:
            self._manejar_error_api(dispatcher, dato_tipo, tracker)

        return self._reset_slots()

    def _formatear_respuesta_papeletas(self, data: Dict[str, Any],
                                       tipo_consulta: str, tracker: Tracker) -> str:
        """Formatea la respuesta de la API de papeletas"""

        body_count = data.get("bodyCount", 0)
        papeletas = data.get("data", [])

        # Obtener el valor consultado para personalizar respuesta
        valor_consultado = ""
        if tipo_consulta == "placa":
            valor_consultado = tracker.get_slot("placa")
        elif tipo_consulta == "dni":
            valor_consultado = tracker.get_slot("dni")
        elif tipo_consulta == "ruc":
            valor_consultado = tracker.get_slot("ruc")

        if body_count == 0 or not papeletas:
            return f"""✅ ¡Excelente noticia! No encontré papeletas pendientes para {tipo_consulta.upper()} **{valor_consultado}**.

🎉 Estás al día con las infracciones de tránsito.

💡 **Tip:** Si crees que deberías tener una papeleta que no aparece, puedes registrarla manualmente en:
📌 https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=9&v=%20"""

        # Respuesta con papeletas encontradas
        cantidad = len(papeletas)
        if cantidad == 1:
            mensaje = f"📋 Encontré **1 papeleta pendiente** para {tipo_consulta.upper()} **{valor_consultado}**:\n\n"
        else:
            mensaje = f"📋 Encontré **{cantidad} papeletas pendientes** para {tipo_consulta.upper()} **{valor_consultado}**:\n\n"

        total = 0
        for i, papeleta in enumerate(papeletas, 1):
            concepto = papeleta.get('concepto', 'N/A')
            falta = papeleta.get('falta', 'N/A').strip()
            documento = papeleta.get('documento', 'N/A').strip()
            fecha_infraccion = papeleta.get('fechainfraccion', 'N/A').strip()
            monto = float(papeleta.get('monto', 0))
            estado = papeleta.get('estado', 'N/A')

            total += monto

            mensaje += f"**🚨 Papeleta #{i}:**\n"
            mensaje += f"• **Tipo de falta:** {falta}\n"
            mensaje += f"• **N° de papeleta:** {documento}\n"
            mensaje += f"• **Fecha de infracción:** {fecha_infraccion}\n"
            mensaje += f"• **Monto:** S/ {monto:.2f}\n"
            mensaje += f"• **Estado:** {estado}\n\n"

        mensaje += f"💰 **Total a pagar:** S/ {total:.2f}\n\n"

        # Recomendaciones personalizadas
        if total > 1000:
            mensaje += "💡 **Recomendación:** El monto es elevado. Te sugiero solicitar facilidades de pago en la Agencia Virtual del SAT para fraccionarlo.\n\n"
        elif total > 500:
            mensaje += "💡 **Tip:** Puedes solicitar facilidades de pago en la Agencia Virtual del SAT para pagar en cuotas.\n\n"

        mensaje += "🔗 **¿Quieres pagar ahora?** Puedes hacerlo en:\n📌 https://www.sat.gob.pe/pagosenlinea/\n\n"
        mensaje += "🏛️ *Consulta oficial del SAT de Lima*"

        return mensaje

    def _manejar_error_api(self, dispatcher: CollectingDispatcher,
                           tipo_consulta: str, tracker: Tracker):
        """Maneja errores de la API de forma amigable"""

        valor_consultado = ""
        if tipo_consulta == "placa":
            valor_consultado = tracker.get_slot("placa")
        elif tipo_consulta == "dni":
            valor_consultado = tracker.get_slot("dni")
        elif tipo_consulta == "ruc":
            valor_consultado = tracker.get_slot("ruc")

        mensaje = f"""😔 Lo siento, tuve un problema técnico al consultar la información para {tipo_consulta.upper()} **{valor_consultado}**.

🔧 Esto puede ocurrir por:
• Mantenimiento del sistema del SAT
• Problemas temporales de conexión
• Alta demanda en el servidor

📱 **Mientras tanto, puedes:**
• Consultar directamente en: https://www.sat.gob.pe/pagosenlinea/
• Intentar nuevamente en unos minutos
• Visitar nuestras oficinas

⏰ ¿Quieres intentarlo de nuevo o necesitas ayuda con algo más?"""

        dispatcher.utter_message(text=mensaje)

    def _manejar_correccion(self, dispatcher: CollectingDispatcher,
                            dato_tipo: str) -> List[Dict[Text, Any]]:
        """Maneja cuando el usuario indica que el dato es incorrecto"""

        mensajes = {
            'placa': "¿Cuál es la placa correcta? Por ejemplo: ABC123, U1A710",
            'dni': "¿Cuál es tu DNI correcto? Debe tener 8 dígitos.",
            'ruc': "¿Cuál es el RUC correcto? Debe tener 11 dígitos."
        }

        mensaje = mensajes.get(dato_tipo, "¿Cuál es el dato correcto?")
        dispatcher.utter_message(text=mensaje)

        # Reset solo el dato específico
        slots_reset = [SlotSet("esperando_confirmacion", False), SlotSet("dato_detectado", None)]

        if dato_tipo == "placa":
            slots_reset.append(SlotSet("placa", None))
        elif dato_tipo == "dni":
            slots_reset.append(SlotSet("dni", None))
        elif dato_tipo == "ruc":
            slots_reset.append(SlotSet("ruc", None))

        return slots_reset

    def _reset_slots(self) -> List[Dict[Text, Any]]:
        """Resetea slots después de completar consulta"""
        return [
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("tipo_consulta_actual", None)
        ]