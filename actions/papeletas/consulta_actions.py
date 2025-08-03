"""
Actions para consulta de papeletas con APIs del SAT
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
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
        """Inicia el proceso de consulta detectando datos disponibles y limpiando context"""

        # Primero revisar entities del último mensaje (tiene prioridad)
        entities = tracker.latest_message.get('entities', [])
        placa_msg = None
        dni_msg = None
        ruc_msg = None

        for entity in entities:
            if entity['entity'] == 'placa':
                placa_msg = entity['value']
            elif entity['entity'] == 'dni':
                dni_msg = entity['value']
            elif entity['entity'] == 'ruc':
                ruc_msg = entity['value']

        # Obtener datos de slots actuales
        placa_slot = tracker.get_slot("placa")
        dni_slot = tracker.get_slot("dni")
        ruc_slot = tracker.get_slot("ruc")

        logger.info(f"📊 Entities del mensaje: placa={placa_msg}, dni={dni_msg}, ruc={ruc_msg}")
        logger.info(f"📊 Slots actuales: placa={placa_slot}, dni={dni_slot}, ruc={ruc_slot}")

        # Determinar qué tipo de consulta es ESTA vez (prioridad a entities del mensaje)
        if placa_msg:
            tipo_actual = "placa"
            valor_actual = placa_msg
        elif dni_msg:
            tipo_actual = "dni"
            valor_actual = dni_msg
        elif ruc_msg:
            tipo_actual = "ruc"
            valor_actual = ruc_msg
        elif placa_slot and not dni_msg and not ruc_msg:
            tipo_actual = "placa"
            valor_actual = placa_slot
        elif dni_slot and not placa_msg and not ruc_msg:
            tipo_actual = "dni"
            valor_actual = dni_slot
        elif ruc_slot and not placa_msg and not dni_msg:
            tipo_actual = "ruc"
            valor_actual = ruc_slot
        else:
            return self._solicitar_datos(dispatcher)

        logger.info(f"🎯 Tipo de consulta detectado: {tipo_actual} = {valor_actual}")

        # Procesar según el tipo detectado
        if tipo_actual == "placa":
            return self._procesar_placa(dispatcher, valor_actual)
        elif tipo_actual == "dni":
            return self._procesar_dni(dispatcher, valor_actual)
        elif tipo_actual == "ruc":
            return self._procesar_ruc(dispatcher, valor_actual)
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
            return self._reset_all_slots()

        # Pedir confirmación
        mensaje = f"Detecté la placa **{placa_limpia}**. ¿Es correcta?"
        dispatcher.utter_message(text=mensaje)

        return [
            # Limpiar otros tipos
            SlotSet("dni", None),
            SlotSet("ruc", None),
            # Configurar para placa
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
            return self._reset_all_slots()

        # Pedir confirmación
        mensaje = f"Detecté el DNI **{dni_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=mensaje)

        return [
            # Limpiar otros tipos
            SlotSet("placa", None),
            SlotSet("ruc", None),
            # Configurar para DNI
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
            return self._reset_all_slots()

        # Pedir confirmación
        mensaje = f"Detecté el RUC **{ruc_limpio}**. ¿Es correcto?"
        dispatcher.utter_message(text=mensaje)

        return [
            # Limpiar otros tipos
            SlotSet("placa", None),
            SlotSet("dni", None),
            # Configurar para RUC
            SlotSet("ruc", ruc_limpio),
            SlotSet("dato_detectado", "ruc"),
            SlotSet("esperando_confirmacion", True)
        ]

    def _solicitar_datos(self, dispatcher: CollectingDispatcher, tracker: Tracker) -> List[Dict[Text, Any]]:
        """Solicita datos cuando no se proporcionaron"""

        # Verificar si el usuario indicó un tipo específico
        mensaje_usuario = tracker.latest_message.get('text', '').lower()

        if 'placa' in mensaje_usuario:
            mensaje = """Perfecto, vamos a consultar por placa vehicular 🚗

Por favor, dime el número de tu placa:
📝 **Ejemplos:** ABC123, U1A710, DEF456"""

        elif 'dni' in mensaje_usuario:
            mensaje = """Perfecto, vamos a consultar por DNI 🆔

Por favor, dime tu número de DNI:
📝 **Formato:** 8 dígitos (ejemplo: 12345678)"""

        elif 'ruc' in mensaje_usuario:
            mensaje = """Perfecto, vamos a consultar por RUC 🏢

Por favor, dime el número de RUC:
📝 **Formato:** 11 dígitos (ejemplo: 20123456789)"""

        else:
            mensaje = """Para consultar tus papeletas necesito uno de estos datos:

🚗 **Placa del vehículo** - Ej: ABC123, U1A710
🆔 **Tu DNI** - 8 dígitos
🏢 **RUC** - 11 dígitos

¿Cuál prefieres proporcionar?"""

        dispatcher.utter_message(text=mensaje)
        return self._reset_all_slots()

    def _reset_all_slots(self) -> List[Dict[Text, Any]]:
        """Resetea todos los slots de datos"""
        return [
            SlotSet("placa", None),
            SlotSet("dni", None),
            SlotSet("ruc", None),
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("tipo_consulta_actual", None)
        ]

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

            # Ofrecer nuevas consultas
            mensaje_adicional = "\n\n💬 **¿Necesitas algo más?**\n• 'Consultar con otro documento' para nueva consulta\n• 'Pagos en línea' para información de pagos\n• 'Finalizar' para cerrar la conversación"
            dispatcher.utter_message(text=mensaje_adicional)
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

        # Reset solo el dato específico pero mantener esperando_confirmacion en false
        return [
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("placa", None),
            SlotSet("dni", None),
            SlotSet("ruc", None)
        ]

    def _reset_slots(self) -> List[Dict[Text, Any]]:
        """Resetea slots después de completar consulta"""
        return [
            SlotSet("esperando_confirmacion", False),
            SlotSet("dato_detectado", None),
            SlotSet("tipo_consulta_actual", None)
        ]