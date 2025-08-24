"""
Actions para actualización de datos del usuario
Preparado para futura integración con CRM
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

logger = logging.getLogger(__name__)


class CRMIntegrationBase:
    """
    Clase base para futura integración con CRM
    Contiene métodos placeholder que serán implementados más adelante
    """

    @staticmethod
    def get_user_data(user_id: str) -> Dict[str, str]:
        """
        Placeholder para obtener todos los datos del usuario desde CRM

        Args:
            user_id: ID del usuario en el sistema

        Returns:
            Dict: Datos actuales del usuario (placeholder)
        """
        logger.info(f"Placeholder: Obteniendo datos para usuario {user_id}")
        return {
            "telefono": "999-XXX-XXX",
            "dni": "XXXXXXXX",
            "email": "usuario@ejemplo.com"
        }

    @staticmethod
    def update_user_data(user_id: str, telefono: str = None, dni: str = None, email: str = None) -> bool:
        """
        Placeholder para actualizar datos del usuario en CRM

        Args:
            user_id: ID del usuario
            telefono: Nuevo teléfono (opcional)
            dni: Nuevo DNI (opcional)
            email: Nuevo email (opcional)

        Returns:
            bool: True si actualización exitosa (placeholder)
        """
        logger.info(f"Placeholder: Actualizando datos para usuario {user_id}")
        if telefono:
            logger.info(f"Nuevo teléfono: {telefono}")
        if dni:
            logger.info(f"Nuevo DNI: {dni}")
        if email:
            logger.info(f"Nuevo email: {email}")
        return True


class ActionActualizarDatos(Action):
    """Action principal para actualizar datos del usuario"""

    def name(self) -> Text:
        return "action_actualizar_datos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("Iniciando proceso de actualización de datos (placeholder)")

        user_id = tracker.sender_id

        # Obtener datos actuales (placeholder)
        datos_actuales = CRMIntegrationBase.get_user_data(user_id)

        message = f"""👤 **ACTUALIZAR MIS DATOS**

📋 **Datos actuales registrados:**

📱 **Teléfono:** {datos_actuales['telefono']}
🆔 **DNI:** {datos_actuales['dni']}
📧 **Correo:** {datos_actuales['email']}



**¿Qué más necesitas?**
• 'Menú principal' - Principales opciones
• 'Oficinas SAT' - Ubicaciones para trámites presenciales"""

        dispatcher.utter_message(text=message)
        return [SlotSet("ultimo_proceso", "actualizar_datos")]


# Instancia global para futura integración CRM
crm_integration = CRMIntegrationBase()