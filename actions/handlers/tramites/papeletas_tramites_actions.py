"""
Actions para trámites administrativos de papeletas
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

from actions.api.sat_client import sat_client

logger = logging.getLogger(__name__)


class BaseTramiteRequisitos(Action):
    """Clase base para trámites que consultan requisitos del TUPA"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = ""  # Debe ser sobrescrito por cada clase hija
        self.tipo_tramite = ""  # "papeletas" o "tributarios"

    def name(self) -> Text:
        # Esta clase base NO debe ser registrada directamente
        return "base_tramite_requisitos_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info(f"Consultando requisitos para: {self.titulo_tramite}")

        # Paso 1: Consultar menú de opciones para obtener ivalor
        menu_response = sat_client.consultar_menu_opcion(self.titulo_tramite)

        if not menu_response or 'ivalor' not in menu_response:
            logger.error(f"No se pudo obtener ivalor para: {self.titulo_tramite}")
            return self._handle_api_error(dispatcher)

        ivalor = menu_response.get('ivalor')
        logger.info(f"ivalor obtenido: {ivalor}")

        # Paso 2: Consultar requisitos del TUPA
        requisitos_response = sat_client.consultar_requisitos_tupa(ivalor)

        if not requisitos_response or not isinstance(requisitos_response, list) or len(requisitos_response) == 0:
            logger.error(f"No se pudieron obtener requisitos para ivalor: {ivalor}")
            return self._handle_api_error(dispatcher)

        # Paso 3: Extraer y formatear el texto de requisitos
        vdetalle = requisitos_response[0].get('vdetalle', '')

        if not vdetalle:
            logger.error(f"vdetalle vacío para ivalor: {ivalor}")
            return self._handle_api_error(dispatcher)

        # Convertir HTML a texto plano
        texto_requisitos = sat_client.format_html_to_text(vdetalle)

        # Paso 4: Enviar mensaje con los requisitos
        dispatcher.utter_message(text=texto_requisitos)

        # Paso 5: Enviar mensaje con enlaces útiles
        mensaje_enlaces = self._get_enlaces_message()
        dispatcher.utter_message(text=mensaje_enlaces)

        return []

    def _get_enlaces_message(self) -> str:
        """Genera mensaje con enlaces útiles según el tipo de trámite"""

        base_message = """**¿Qué más necesitas?**
- 'Menú principal' - Otras opciones
- 'Finalizar chat'"""

        if self.tipo_tramite == "papeletas":
            return f"""📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

{base_message}"""

        else:  # tributarios
            return f"""📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

{base_message}"""

    def _handle_api_error(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        """Maneja errores de la API"""

        message = f"""😔 Lo siento, tuve un problema técnico al consultar los requisitos de este trámite.

🔧 **Esto puede ocurrir por:**
- Mantenimiento del sistema del SAT
- Problemas temporales de conexión

📱 **Mientras tanto puedes:**
- Consultar directamente en: https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA
- Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
- 'Otros trámites' - Ver otras opciones de trámites
- 'Menú principal' - Volver al menú principal
- 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesRecursoReconsideracion(BaseTramiteRequisitos):
    """Action para recurso de reconsideración de papeletas"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "RECURSO DE RECONSIDERACIÓN"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_recurso_reconsideracion"


class ActionTramitesDescargoInfracciones(BaseTramiteRequisitos):
    """Action para descarga de infracciones"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "DESCARGO DE INFRACCIONES"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_descargo_infracciones"


class ActionTramitesApelacionPapeletas(BaseTramiteRequisitos):
    """Action para apelación de papeletas"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "RECURSO DE APELACIÓN"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_apelacion_papeletas"


class ActionTramitesPrescripcionPapeletas(BaseTramiteRequisitos):
    """Action para prescripción de papeletas"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "PRESCRIPCIÓN"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_prescripcion_papeletas"


class ActionTramitesDevolucionPapeletas(BaseTramiteRequisitos):
    """Action para devolución y/o compensación de papeletas"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "DEVOLUCIÓN Y/O COMPENSACIÓN"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_devolucion_papeletas"


class ActionTramitesTerceriaRequisitos(BaseTramiteRequisitos):
    """Action para tercería de propiedad (requisitos papeletas)"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "TERCERIA DE PROPIEDAD"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_terceria_requisitos"


class ActionTramitesSuspensionRequisitos(BaseTramiteRequisitos):
    """Action para suspensión de cobranza coactiva (requisitos papeletas)"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "SUSPENSION DE LA COBRANZA COACTIVA"
        self.tipo_tramite = "papeletas"

    def name(self) -> Text:
        return "action_tramites_suspension_requisitos"