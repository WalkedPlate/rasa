"""
Actions para actualización de datos del usuario con integración al backend
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import re

from ..core.backend_client import backend_client
from ..core.validators import validator

logger = logging.getLogger(__name__)


class ActionActualizarDatos(Action):
    """Action para mostrar y gestionar datos del usuario"""

    def name(self) -> Text:
        return "action_actualizar_datos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Iniciando consulta de datos del ciudadano")

        # Obtener número de teléfono del sender_id
        phone_number = tracker.sender_id

        # Validar formato del número de teléfono
        es_valido, phone_limpio = validator.validate_phone_number(phone_number)

        if not es_valido:
            logger.warning(f"Número de teléfono inválido: {phone_number}")
            message = f"""❌ **Error de sistema**

El número de teléfono {phone_number} no tiene un formato válido.

**Formato esperado:** 51XXXXXXXXX (11 dígitos empezando en 51)

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones"""

            dispatcher.utter_message(text=message)
            return []

        # Consultar datos del ciudadano
        try:
            datos_ciudadano = backend_client.get_citizen_data(phone_limpio)

            if datos_ciudadano is None:
                # Ciudadano no registrado
                return self._handle_unregistered_citizen(dispatcher, phone_limpio)
            else:
                # Ciudadano encontrado - mostrar datos actuales
                return self._show_current_data(dispatcher, datos_ciudadano)

        except Exception as e:
            logger.error(f"Error consultando datos del ciudadano {phone_limpio}: {e}")
            return self._handle_backend_error(dispatcher)

    def _handle_unregistered_citizen(self, dispatcher: CollectingDispatcher,
                                   phone_number: str) -> List[Dict[Text, Any]]:
        """Maneja el caso cuando el ciudadano no está registrado"""

        logger.info(f"Ciudadano no registrado: {phone_number}")

        message = f"""📋 **No estás registrado en el sistema**

Tu número {phone_number} no se encuentra registrado.

**Para registrarte necesitas:**
• Acercarte a las oficinas del SAT
• Contactarnos por correo: asuservicio@sat.gob.pe

**¿Qué más necesitas?**
• 'Oficinas SAT' - Ubicaciones para registro presencial
• 'Menú principal' - Otras opciones
• 'Papeletas' - Consultar multas
• 'Impuestos' - Consultar deuda tributaria"""

        dispatcher.utter_message(text=message)
        return []

    def _show_current_data(self, dispatcher: CollectingDispatcher,
                          datos_ciudadano: Dict[str, Any]) -> List[Dict[Text, Any]]:
        """Muestra los datos actuales del ciudadano"""

        logger.info("Mostrando datos actuales del ciudadano")

        # Extraer datos del response del backend
        full_name = datos_ciudadano.get('fullName', 'No disponible')
        document_type = datos_ciudadano.get('documentType', 'No disponible')
        document_number = datos_ciudadano.get('documentNumber', 'No disponible')
        phone_number = datos_ciudadano.get('phoneNumber', 'No disponible')

        message = f"""👤 **TUS DATOS ACTUALES**

📋 **Información registrada:**
• **Nombre completo:** {full_name}
• **Tipo de documento:** {document_type}
• **Número de documento:** {document_number}
• **Teléfono:** {phone_number}

**¿Deseas actualizar algún dato?**
• Escribe **"Cambiar nombre"** - Para actualizar tu nombre
• Escribe **"Cambiar documento"** - Para actualizar DNI/documento
• Escribe **"Mis datos están correctos"** - Si no necesitas cambios

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Papeletas' - Consultar multas
• 'Impuestos' - Consultar deuda tributaria"""

        dispatcher.utter_message(text=message)
        return [SlotSet("datos_actuales", datos_ciudadano)]

    def _handle_backend_error(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Maneja errores de conexión con el backend"""

        logger.error("Error de conexión con el backend")

        message = f"""😔 **Error temporal del sistema**

No pudimos consultar tus datos en este momento.

🔧 **Esto puede ocurrir por:**
• Mantenimiento del sistema
• Problemas temporales de conexión

**Por favor intenta nuevamente en unos minutos.**

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Papeletas' - Consultar multas
• 'Impuestos' - Consultar deuda tributaria
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionActualizarNombre(Action):
    """Action para actualizar el nombre del ciudadano"""

    def name(self) -> Text:
        return "action_actualizar_nombre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Solicitando actualización de nombre")

        message = f"""✏️ **Actualizar nombre**

**Escribe tu nombre completo nuevo.**

**Ejemplo:** Juan Carlos Pérez López

*(El nombre debe tener al menos 2 palabras)*"""

        dispatcher.utter_message(text=message)
        return [SlotSet("esperando_nuevo_nombre", True)]


class ActionProcesarNuevoNombre(Action):
    """Action para procesar el nuevo nombre proporcionado"""

    def name(self) -> Text:
        return "action_procesar_nuevo_nombre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Procesando nuevo nombre del ciudadano")

        nuevo_nombre = tracker.latest_message.get('text', '').strip()

        # Validar nombre
        if not nuevo_nombre or len(nuevo_nombre.split()) < 2:
            message = f"""❌ **Nombre inválido**

El nombre debe tener al menos 2 palabras.

**Ejemplo:** Juan Carlos Pérez López

**Intenta nuevamente o escribe 'cancelar' para volver.**"""

            dispatcher.utter_message(text=message)
            return []

        phone_number = tracker.sender_id
        datos_actuales = tracker.get_slot("datos_actuales") or {}

        # Preparar datos para actualización
        citizen_data = {
            "phoneNumber": phone_number,
            "fullName": nuevo_nombre,
            "documentType": datos_actuales.get('documentType', 'DNI'),
            "documentNumber": datos_actuales.get('documentNumber', '')
        }

        # Actualizar en el backend
        try:
            actualizacion_exitosa = backend_client.update_citizen_data(citizen_data)

            if actualizacion_exitosa:
                message = f"""✅ **Nombre actualizado exitosamente**

**Nuevo nombre:** {nuevo_nombre}

**¿Qué más necesitas?**
• 'Actualizar datos' - Ver datos actualizados
• 'Cambiar documento' - Actualizar DNI/documento
• 'Menú principal' - Otras opciones"""

                dispatcher.utter_message(text=message)
                logger.info(f"Nombre actualizado exitosamente: {phone_number}")
            else:
                message = f"""❌ **Error actualizando nombre**

No pudimos actualizar tu nombre en este momento.

**Intenta nuevamente más tarde.**

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

                dispatcher.utter_message(text=message)
                logger.error(f"Error actualizando nombre: {phone_number}")

        except Exception as e:
            logger.error(f"Error actualizando nombre para {phone_number}: {e}")
            dispatcher.utter_message(text="❌ Error temporal del sistema. Intenta nuevamente más tarde.")

        return [
            SlotSet("esperando_nuevo_nombre", False),
            SlotSet("datos_actuales", None)
        ]


class ActionActualizarDocumento(Action):
    """Action para actualizar documento y tipo de documento del ciudadano"""

    def name(self) -> Text:
        return "action_actualizar_documento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Solicitando actualización de documento")

        message = f"""📄 **Actualizar documento**

**Paso 1: Escribe el tipo de documento**

**Opciones disponibles:**
• DNI
• CE (Carnet de Extranjería)
• OTRO

**Ejemplo:** DNI"""

        dispatcher.utter_message(text=message)
        return [SlotSet("esperando_tipo_documento", True)]


class ActionProcesarTipoDocumento(Action):
    """Action para procesar el tipo de documento proporcionado"""

    def name(self) -> Text:
        return "action_procesar_tipo_documento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Procesando tipo de documento")

        tipo_documento = tracker.latest_message.get('text', '').strip().upper()

        # Validar tipo de documento
        tipos_validos = ['DNI', 'CE', 'OTRO']

        if tipo_documento not in tipos_validos:
            message = f"""❌ **Tipo de documento inválido**

**Tipos válidos:**
• DNI
• CE
• OTRO

**Intenta nuevamente o escribe 'cancelar' para volver.**"""

            dispatcher.utter_message(text=message)
            return []

        message = f"""✅ **Tipo de documento: {tipo_documento}**

**Paso 2: Ahora escribe el número de documento**

**Formato según el tipo:**
• **DNI:** 8 dígitos (ej: 12345678)
• **CE:** 9-12 dígitos (ej: 123456789)
• **OTRO:** Hasta 15 caracteres alfanuméricos

**Ejemplo:** 12345678"""

        dispatcher.utter_message(text=message)
        return [
            SlotSet("esperando_tipo_documento", False),
            SlotSet("esperando_numero_documento", True),
            SlotSet("nuevo_tipo_documento", tipo_documento)
        ]


class ActionProcesarNumeroDocumento(Action):
    """Action para procesar el número de documento y actualizar"""

    def name(self) -> Text:
        return "action_procesar_numero_documento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Procesando número de documento")

        numero_documento = tracker.latest_message.get('text', '').strip()
        tipo_documento = tracker.get_slot("nuevo_tipo_documento")

        # Validar número según tipo
        es_valido = self._validar_numero_documento(numero_documento, tipo_documento)

        if not es_valido:
            message = f"""❌ **Número de documento inválido para {tipo_documento}**

**Formato correcto:**
• **DNI:** 8 dígitos exactos
• **CE:** 9-12 dígitos
• **OTRO:** Hasta 15 caracteres alfanuméricos

**Intenta nuevamente o escribe 'cancelar' para volver.**"""

            dispatcher.utter_message(text=message)
            return []

        # Actualizar en el backend
        phone_number = tracker.sender_id
        datos_actuales = tracker.get_slot("datos_actuales") or {}

        nombre_completo = datos_actuales.get('fullName', '')
        primer_nombre = nombre_completo.split()[0] if nombre_completo else 'Usuario'

        # Extraer primer nombre
        nombre_completo = datos_actuales.get('fullName', '')
        primer_nombre = nombre_completo.split()[0] if nombre_completo else 'Usuario'

        citizen_data = {
            "phoneNumber": phone_number,
            "fullName": datos_actuales.get('fullName', ''),
            "documentType": tipo_documento,
            "documentNumber": numero_documento
        }

        try:
            actualizacion_exitosa = backend_client.update_citizen_data(citizen_data)

            if actualizacion_exitosa:
                message = f"""✅ **Documento actualizado exitosamente**

**Nuevo documento:** {tipo_documento} {numero_documento}

**¿Qué más necesitas?**
• 'Actualizar datos' - Ver datos actualizados
• 'Cambiar nombre' - Actualizar nombre
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

                dispatcher.utter_message(text=message)
                logger.info(f"Documento actualizado exitosamente: {phone_number}")
            else:
                message = f"""❌ **Error actualizando documento**

No pudimos actualizar tu documento en este momento.

**Intenta nuevamente más tarde.**

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones"""

                dispatcher.utter_message(text=message)
                logger.error(f"Error actualizando documento: {phone_number}")

        except Exception as e:
            logger.error(f"Error actualizando documento para {phone_number}: {e}")
            dispatcher.utter_message(text="❌ Error temporal del sistema. Intenta nuevamente más tarde.")

        return [
            SlotSet("esperando_numero_documento", False),
            SlotSet("nuevo_tipo_documento", None),
            SlotSet("datos_actuales", None)
        ]

    def _validar_numero_documento(self, numero: str, tipo: str) -> bool:
        """Valida formato del número según tipo de documento"""

        if not numero:
            return False

        if tipo == "DNI":
            # DNI: exactamente 8 dígitos
            numero_limpio = re.sub(r'[^0-9]', '', numero)
            return len(numero_limpio) == 8 and numero_limpio.isdigit()

        elif tipo == "CE":
            # CE: 9-12 dígitos
            numero_limpio = re.sub(r'[^0-9]', '', numero)
            return 9 <= len(numero_limpio) <= 12 and numero_limpio.isdigit()

        elif tipo == "OTRO":
            # OTRO: hasta 15 caracteres alfanuméricos
            numero_limpio = re.sub(r'[^A-Z0-9]', '', numero.upper())
            return 1 <= len(numero_limpio) <= 15 and numero_limpio.isalnum()

        return False