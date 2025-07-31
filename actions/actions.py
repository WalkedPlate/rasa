from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted, FollowupAction
import requests
import re
import json
import time
from datetime import datetime, timedelta

# ========== CLASE DE AUTENTICACIÓN ==========
class SATAuthManager:
    """Maneja la autenticación automática con la API del SAT"""
    
    def __init__(self):
        self.token = None
        self.token_expiry = None
        self.auth_url = "https://ws.sat.gob.pe/auth/login"
        self.credentials = {
            "client_id": "ChatBootSat",
            "client_secret": "4qp3hETQRbdyt20o6762a33dMEpr3Bqx",
            "usuario": "usrchatbootsat",
            "clave": "PQb%qd72E@%4cCnmkyT*"
        }
    
    def get_valid_token(self):
        """Obtiene un token válido, renovándolo si es necesario"""
        if self.token is None or self.is_token_expired():
            self.refresh_token()
        return self.token
    
    def is_token_expired(self):
        """Verifica si el token ha expirado"""
        if self.token_expiry is None:
            return True
        return datetime.now() >= (self.token_expiry - timedelta(minutes=1))
    
    def refresh_token(self):
        """Obtiene un nuevo token de la API"""
        try:
            response = requests.post(
                self.auth_url, 
                json=self.credentials,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                expires_in = data.get("expires_in", 900)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                print(f"✅ Token renovado exitosamente, expira en {expires_in} segundos")
            else:
                print(f"❌ Error obteniendo token: {response.status_code}")
                self.token = None
                
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            self.token = None

# Instancia global del manejador de autenticación
auth_manager = SATAuthManager()

# ========== ACCIÓN: CONFIRMAR PLACA ==========
class ActionConfirmarPlaca(Action):
    """Confirma la placa detectada con el usuario"""

    def name(self) -> Text:
        return "action_confirmar_placa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print(f"🔍 DEBUG: action_confirmar_placa ejecutándose")
        
        placa = tracker.get_slot("placa")
        print(f"🔍 DEBUG: placa del slot = {placa}")
        
        # También revisar las entidades del último mensaje
        latest_message = tracker.latest_message
        entities = latest_message.get('entities', [])
        print(f"🔍 DEBUG: entidades detectadas = {entities}")
        
        # Buscar entidad placa en el mensaje
        placa_entity = None
        for entity in entities:
            if entity.get('entity') == 'placa':
                placa_entity = entity.get('value')
                print(f"🔍 DEBUG: placa encontrada en entidades = {placa_entity}")
                break
        
        # Usar la placa de la entidad si no hay en slot
        if not placa and placa_entity:
            placa = placa_entity
            print(f"🔍 DEBUG: usando placa de entidad = {placa}")
        
        if not placa:
            print(f"🔍 DEBUG: No hay placa disponible")
            dispatcher.utter_message(text="No detecté ninguna placa. ¿Podrías proporcionarla nuevamente? Por ejemplo: ABC123")
            return [SlotSet("esperando_confirmacion", False)]
        
        # Limpiar y validar la placa
        placa_limpia = self.limpiar_placa(placa)
        print(f"🔍 DEBUG: placa limpia = {placa_limpia}")
        
        # Mensaje de confirmación personalizado
        mensaje = f"""Perfecto, detecté la placa **{placa_limpia}**. 

¿Es correcto? 🚗

Responde 'sí' para continuar o 'no' si necesitas corregirla."""
        
        print(f"🔍 DEBUG: enviando mensaje de confirmación")
        dispatcher.utter_message(text=mensaje)
        
        return [
            SlotSet("placa_detectada", placa_limpia),
            SlotSet("esperando_confirmacion", True),
            SlotSet("placa", placa_limpia)
        ]
    
    def limpiar_placa(self, placa: str) -> str:
        """Limpia y formatea la placa"""
        if not placa:
            return ""
        placa_limpia = placa.strip().upper()
        placa_limpia = re.sub(r'[^A-Z0-9]', '', placa_limpia)
        return placa_limpia

# ========== ACCIÓN: PROCESAR CONFIRMACIÓN ==========
class ActionProcesarConfirmacion(Action):
    """Procesa la confirmación del usuario (sí/no)"""

    def name(self) -> Text:
        return "action_procesar_confirmacion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.latest_message['intent']['name']
        placa_detectada = tracker.get_slot("placa_detectada")
        
        print(f"🔍 DEBUG: procesando confirmación - intent = {intent}")
        print(f"🔍 DEBUG: placa_detectada = {placa_detectada}")
        
        if intent == "confirm_yes":
            # Usuario confirmó la placa
            dispatcher.utter_message(text="¡Excelente! Procediendo con la consulta... 🔍")
            
            return [
                SlotSet("placa_confirmada", True),
                SlotSet("esperando_confirmacion", False),
                SlotSet("placa", placa_detectada),
                FollowupAction("action_consultar_papeletas")
            ]
        
        elif intent == "confirm_no":
            # Usuario rechazó la placa
            dispatcher.utter_message(
                text="Entiendo, la placa no es correcta. 🔧\n\n¿Cuál es la placa correcta?\n\n📝 **Ejemplo:** ABC123, U1A710, etc."
            )
            
            return [
                SlotSet("placa_confirmada", False),
                SlotSet("esperando_confirmacion", False),
                SlotSet("placa", None),
                SlotSet("placa_detectada", None)
            ]
        
        else:
            # Intent no reconocido durante confirmación
            dispatcher.utter_message(
                text=f"Para la placa **{placa_detectada}**, necesito que respondas:\n\n✅ 'Sí' si es correcta\n❌ 'No' si necesitas corregirla"
            )
            
            return [SlotSet("esperando_confirmacion", True)]

# ========== ACCIÓN: PROCESAR CORRECCIÓN ==========
class ActionProcesarCorreccion(Action):
    """Procesa cuando el usuario proporciona una corrección"""

    def name(self) -> Text:
        return "action_procesar_correccion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtener la nueva placa del mensaje
        entities = tracker.latest_message.get('entities', [])
        nueva_placa = None
        
        for entity in entities:
            if entity['entity'] == 'placa':
                nueva_placa = entity['value']
                break
        
        if nueva_placa:
            placa_limpia = self.limpiar_placa(nueva_placa)
            
            return [
                SlotSet("placa", placa_limpia),
                SlotSet("placa_detectada", placa_limpia),
                SlotSet("esperando_confirmacion", False),
                FollowupAction("action_confirmar_placa")
            ]
        else:
            dispatcher.utter_message(
                text="No detecté una placa en tu mensaje. 🤔\n\nPor favor, proporciona la placa correcta.\n\n📝 **Ejemplo:** ABC123, U1A710"
            )
            return [SlotSet("esperando_confirmacion", False)]
    
    def limpiar_placa(self, placa: str) -> str:
        """Limpia y formatea la placa"""
        if not placa:
            return ""
        placa_limpia = placa.strip().upper()
        placa_limpia = re.sub(r'[^A-Z0-9]', '', placa_limpia)
        return placa_limpia

# ========== ACCIÓN: CAMBIAR CONSULTA ==========
class ActionCambiarConsulta(Action):
    """Maneja cambios inteligentes de consulta"""

    def name(self) -> Text:
        return "action_cambiar_consulta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje_usuario = tracker.latest_message.get('text', '').lower()
        
        # Detectar qué tipo de consulta quiere hacer
        if any(palabra in mensaje_usuario for palabra in ['pago', 'pagar', 'tarjeta', 'online']):
            dispatcher.utter_message(text="Perfecto, cambiamos a consulta de pagos. 💳")
            return [
                SlotSet("consulta_anterior", "papeletas"),
                SlotSet("esperando_confirmacion", False),
                SlotSet("placa", None),
                SlotSet("placa_detectada", None),
                FollowupAction("action_consultar_pagos")
            ]
            
        elif any(palabra in mensaje_usuario for palabra in ['impuesto', 'predial', 'vehicular', 'dni', 'tributario']):
            dispatcher.utter_message(text="Perfecto, cambiamos a consulta de impuestos. 🏠")
            return [
                SlotSet("consulta_anterior", "papeletas"),
                SlotSet("esperando_confirmacion", False),
                SlotSet("placa", None),
                SlotSet("placa_detectada", None),
                FollowupAction("action_consultar_impuestos")
            ]
        
        else:
            # Consulta genérica, ofrecer opciones
            mensaje = """Entiendo que quieres hacer otra consulta. ¿Qué te interesa?

🚗 **Papeletas** - Di "consultar papeletas" 
💳 **Pagos en línea** - Di "como pagar"
🏠 **Impuestos** - Di "consultar impuestos"

O simplemente dime qué necesitas en tus propias palabras."""
            
            dispatcher.utter_message(text=mensaje)
            
            return [
                SlotSet("consulta_anterior", "papeletas"),
                SlotSet("esperando_confirmacion", False),
                SlotSet("placa", None),
                SlotSet("placa_detectada", None)
            ]

# ========== ACCIÓN: FINALIZAR CHAT ==========
class ActionFinalizarChat(Action):
    """Finaliza la conversación de manera elegante"""

    def name(self) -> Text:
        return "action_finalizar_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        
        # Mensaje personalizado de despedida
        mensaje = f"""¡Gracias por usar el SAT de Lima! 👋

Tu conversación ha sido guardada exitosamente.

📞 **¿Necesitas más ayuda?** Escribe 'hola' cuando regreses
🌐 **Web del SAT:** www.sat.gob.pe
📱 **Mesa de partes digital:** Para trámites online

¡Que tengas un excelente día! 😊"""
        
        dispatcher.utter_message(text=mensaje)
        
        # Log para el sistema
        print(f"💾 Conversación finalizada para usuario: {sender_id} - {datetime.now()}")
        
        return [Restarted()]

# ========== ACCIÓN: CONSULTAR PAPELETAS ==========
class ActionConsultarPapeletas(Action):
    """Consulta papeletas con API real del SAT y validación mejorada"""

    def name(self) -> Text:
        return "action_consultar_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        placa = tracker.get_slot("placa")
        
        if not placa:
            return [FollowupAction("utter_ask_placa")]
        
        # Limpiar y validar la placa
        placa_limpia = self.limpiar_placa(placa)
        
        if not self.validar_placa(placa_limpia):
            mensaje = f"""La placa '{placa}' no tiene un formato válido. 🤔

✅ **Formatos correctos:**
• ABC123 (clásico)
• AB1234 (clásico)  
• U1A710 (nuevo formato)
• A1B234 (nuevo formato)

¿Podrías verificar y proporcionarla nuevamente?"""
            
            dispatcher.utter_message(text=mensaje)
            return [SlotSet("placa", None)]
        
        # Consultar API real del SAT
        try:
            dispatcher.utter_message(text=f"🔍 Perfecto, estoy consultando las papeletas para la placa **{placa_limpia}** en el sistema del SAT... Un momentito.")
            
            resultado = self.consultar_api_sat(placa_limpia)
            if resultado is not None:
                mensaje = self.formatear_respuesta_natural(resultado, placa_limpia, tracker)
                dispatcher.utter_message(text=mensaje)
                
                # Preguntar si necesita algo más
                mensaje_adicional = "\n\n💬 **¿Necesitas algo más?**\n• Dime 'pagos' para ver opciones de pago\n• Dime 'impuestos' para consultar deuda tributaria\n• Dime 'finalizar' para cerrar la conversación"
                dispatcher.utter_message(text=mensaje_adicional)
                
            else:
                self.manejar_error_api(dispatcher, placa_limpia)
        
        except Exception as e:
            print(f"Error consultando API del SAT: {e}")
            self.manejar_error_api(dispatcher, placa_limpia)
        
        return [
            SlotSet("placa_confirmada", True),
            SlotSet("esperando_confirmacion", False)
        ]
    
    def consultar_api_sat(self, placa: str):
        """Consulta la API real del SAT con autenticación automática"""
        
        token = auth_manager.get_valid_token()
        if not token:
            print("❌ No se pudo obtener token de autenticación")
            return None
        
        url = f"https://ws.sat.gob.pe/saldomatico/saldomatico/chatboot/3/{placa}/0/10/11"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "IP": "172.168.1.1"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa: {data.get('bodyCount', 0)} registros")
                return data
            elif response.status_code == 401:
                # Token expirado, renovar
                auth_manager.token = None
                token = auth_manager.get_valid_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    response = requests.get(url, headers=headers, timeout=30, verify=False)
                    if response.status_code == 200:
                        return response.json()
                return None
            else:
                print(f"❌ Error API SAT: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"🌐 Error de conexión: {e}")
            return None
    
    def formatear_respuesta_natural(self, data: dict, placa: str, tracker: Tracker) -> str:
        """Formatea la respuesta de forma natural y personalizada"""
        
        body_count = data.get("bodyCount", 0)
        papeletas = data.get("data", [])
        
        if body_count == 0 or not papeletas:
            return f"✅ ¡Excelente noticia! No encontré papeletas pendientes para la placa **{placa}**.\n\n🎉 Tu vehículo está al día con las infracciones de tránsito.\n\n💡 **Tip:** Si crees que deberías tener una papeleta que no aparece, puedes registrarla manualmente en: https://www.sat.gob.pe/websitev8/Popupv2.aspx?t=9&v=%20"
        
        # Respuesta personalizada según número de papeletas
        if len(papeletas) == 1:
            mensaje = f"📋 He revisado el sistema y encontré **1 papeleta pendiente** para la placa **{placa}**.\n\n"
        else:
            mensaje = f"📋 He revisado el sistema y encontré **{len(papeletas)} papeletas pendientes** para la placa **{placa}**.\n\n"
        
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
            mensaje += "💡 **Recomendación:** El monto es elevado. Te sugiero solicitar facilidades de pago o un compromiso de pago en la Agencia Virtual del SAT para fraccionarlo.\n\n"
        elif total > 500:
            mensaje += "💡 **Tip:** Como el monto es considerable, puedes solicitar facilidades de pago o un compromiso de pago en la Agencia Virtual del SAT.\n\n"
        
        mensaje += "🔗 **¿Quieres pagar ahora?** Puedes hacerlo en: https://www.sat.gob.pe/pagosenlinea/\n"
        mensaje += "🏛️ *Consulta oficial del SAT de Lima*"
        
        return mensaje
    
    def manejar_error_api(self, dispatcher: CollectingDispatcher, placa: str):
        """Maneja errores de la API de forma amigable"""
        mensaje = f"""😔 Lo siento, tuve un problema técnico al consultar la información de la placa **{placa}**.

🔧 Esto puede ocurrir por:
• Mantenimiento del sistema del SAT
• Problemas temporales de conexión
• Alta demanda en el servidor

📱 **Mientras tanto, puedes:**
• Consultar directamente en: https://www.sat.gob.pe/pagosenlinea/
• Intentar nuevamente en unos minutos
• Visitar nuestras oficinas

⏰ ¿Quieres que lo intente de nuevo o prefieres hacer otra consulta?"""
        
        dispatcher.utter_message(text=mensaje)
    
    def limpiar_placa(self, placa: str) -> str:
        """Limpia y formatea la placa"""
        if not placa:
            return ""
        placa_limpia = placa.strip().upper()
        placa_limpia = re.sub(r'[^A-Z0-9]', '', placa_limpia)
        return placa_limpia
    
    def validar_placa(self, placa: str) -> bool:
        """Valida todos los formatos de placas peruanas"""
        if not placa:
            return False
        
        # Formatos de placas peruanas actualizados
        patrones = [
            r'^[A-Z]{3}[0-9]{3}$',      # ABC123 (clásico)
            r'^[A-Z]{2}[0-9]{4}$',      # AB1234 (clásico)  
            r'^[A-Z][0-9][A-Z][0-9]{3}$', # A1B234 (nuevo formato)
            r'^[A-Z]{2}[0-9][A-Z][0-9]{2}$', # AB1C23 (variante)
            r'^T[A-Z]{2}[0-9]{3}$',     # TAXI
            r'^S[A-Z]{2}[0-9]{3}$',     # SERVICIO
        ]
        
        return any(re.match(patron, placa) for patron in patrones)

# ========== ACCIÓN: CONSULTAR PAGOS ==========
class ActionConsultarPagos(Action):
    """Información sobre pagos en línea con respuestas mejoradas"""

    def name(self) -> Text:
        return "action_consultar_pagos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        placa_anterior = tracker.get_slot("placa")
        
        if placa_anterior:
            mensaje = f"""💳 ¡Perfecto! Te ayudo con los pagos en línea para tu placa **{placa_anterior}**.

🌐 **La forma más fácil es por internet:**
https://www.sat.gob.pe/pagosenlinea/

💰 **Puedes pagar con:**
• 💳 Tarjetas Visa, Mastercard, American Express
• 📱 Yape (¡súper rápido!)
• 🏦 Banca por Internet de cualquier banco
• 🏪 Agentes y tiendas autorizadas

💡 **¿El monto es alto?** No te preocupes, tienes opciones:
• Compromiso de pago (cuotas)
• Fraccionamiento de deuda
• Descuentos por pronto pago

🔗 **Agencia Virtual:** https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

¿Necesitas ayuda con algún paso específico del pago?"""
        else:
            mensaje = """💳 ¡Perfecto! Te ayudo con los pagos en línea del SAT.

🌐 **La forma más fácil es por internet:**
https://www.sat.gob.pe/pagosenlinea/

💰 **Puedes pagar con:**
• 💳 Tarjetas Visa, Mastercard, American Express
• 📱 Yape (¡súper rápido!)
• 🏦 Banca por Internet de cualquier banco
• 🏪 Agentes y tiendas autorizadas

📄 **¿Qué puedes pagar?**
• Papeletas de tránsito
• Impuesto de tu casa (predial)
• Impuesto de tu carro (vehicular)
• Alcabala (cuando compras/vendes propiedades)

💡 **¿El monto es alto?** No te preocupes, tienes opciones:
• Compromiso de pago (cuotas)
• Fraccionamiento de deuda
• Descuentos por pronto pago

🤔 **¿Necesitas ayuda específica?** Dime tu placa o DNI y te consulto la deuda exacta."""
        
        dispatcher.utter_message(text=mensaje)
        
        # Preguntar si necesita algo más
        mensaje_adicional = "\n\n💬 **¿Te ayudo con algo más?**\n• 'Consultar papeletas' si quieres ver tus multas\n• 'Consultar impuestos' para deuda tributaria\n• 'Finalizar' para cerrar la conversación"
        dispatcher.utter_message(text=mensaje_adicional)
        
        return []

# ========== ACCIÓN: CONSULTAR IMPUESTOS ==========
class ActionConsultarImpuestos(Action):
    """Consulta impuestos con respuestas más personalizadas"""

    def name(self) -> Text:
        return "action_consultar_impuestos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dni = tracker.get_slot("dni")
        
        if not dni:
            return [FollowupAction("utter_ask_dni")]
        
        # Validar DNI
        if not self.validar_dni(dni):
            dispatcher.utter_message(text=f"El DNI '{dni}' no tiene el formato correcto. Debe tener 8 dígitos. ¿Podrías verificarlo?")
            return [SlotSet("dni", None)]
        
        mensaje = f"""🏠 ¡Listo! He consultado tus impuestos en el sistema del SAT para el DNI **{dni}**.

📊 **Aquí está tu resumen:**

**🏡 IMPUESTO PREDIAL (de tu casa/terreno):**
• 2024: S/ 450.00 (⏰ Pendiente)
• 2023: S/ 0.00 (✅ Pagado)

**🚗 IMPUESTO VEHICULAR (de tu carro):**
• 2024: S/ 320.00 (⏰ Pendiente)  
• 2023: S/ 0.00 (✅ Pagado)

💰 **Total que debes:** S/ 770.00

🎯 **¿Cómo pagar?**
• Online: https://www.sat.gob.pe/pagosenlinea/
• En cuotas: Solicita facilidades de pago

📋 **Ver detalles completos:**
• Predial: https://www.sat.gob.pe/websitev9/TributosMultas/PredialyArbitrios/CuadernilloTributario
• Vehicular: https://www.sat.gob.pe/websitev9/TributosMultas/ImpuestoVehicular/CuadernilloTributario

🎁 **¿Eres pensionista o adulto mayor?** Puedes acceder a descuentos especiales."""
        
        dispatcher.utter_message(text=mensaje)
        
        # Preguntar si necesita algo más
        mensaje_adicional = "\n\n💬 **¿Necesitas algo más?**\n• 'Pagos' para ver opciones de pago\n• 'Papeletas' para consultar multas\n• 'Finalizar' para cerrar la conversación"
        dispatcher.utter_message(text=mensaje_adicional)
        
        return [SlotSet("dni", dni)]
    
    def validar_dni(self, dni: str) -> bool:
        """Valida formato de DNI peruano"""
        if not dni:
            return False
        dni_limpio = re.sub(r'[^0-9]', '', dni)
        return len(dni_limpio) == 8 and dni_limpio.isdigit()
