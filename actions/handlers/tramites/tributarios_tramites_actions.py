"""
Actions para trámites administrativos tributarios
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
        return "base_tramite_requisitos_tributarios"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info(f"Consultando requisitos para: {self.titulo_tramite}")

        # Paso 1: Consultar menú de opciones para obtener ivalor
        menu_response = sat_client.consultar_menu_opcion(
            self.titulo_tramite,
            tipo_tramite="tributarios"
        )

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

📱 **Mientras tanto puedes:**
- Consultar directamente en: https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA
- Intentar nuevamente en unos minutos

**¿Qué más necesitas?**
- 'Otros trámites' - Ver otras opciones de trámites
- 'Menú principal' - Volver al menú principal
- 'Finalizar chat'"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesPredialRequisitos(BaseTramiteRequisitos):
    """Action para requisitos de declaración predial"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "DECLARACIÓN DEL IMPUESTO PREDIAL"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_predial_requisitos"


class ActionTramitesVehicularRequisitos(BaseTramiteRequisitos):
    """Action para requisitos de declaración vehicular"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "DECLARACIÓN DEL IMPUESTO VEHICULAR"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_vehicular_requisitos"


class ActionTramitesAlcabalaRequisitos(BaseTramiteRequisitos):
    """Action para requisitos de liquidación de alcabala"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "LIQUIDACIÓN DE ALCABALA"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_alcabala_requisitos"


class ActionTramitesReclamacionTributaria(BaseTramiteRequisitos):
    """Action para recurso de reclamación tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "RECURSO DE RECLAMACIÓN"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_reclamacion_tributaria"


class ActionTramitesPrescripcionTributaria(BaseTramiteRequisitos):
    """Action para prescripción tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "SOLICITUD DE PRESCRIPCIÓN"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_prescripcion_tributaria"


class ActionTramitesDevolucionTributaria(BaseTramiteRequisitos):
    """Action para devolución tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "SOLICITUD DE DEVOLUCIÓN / COMPENSACIÓN"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_devolucion_tributaria"


class ActionTramitesApelacionTributaria(BaseTramiteRequisitos):
    """Action para apelación tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "RECURSO DE APELACIÓN"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_apelacion_tributaria"


class ActionTramitesTerceriaTributaria(BaseTramiteRequisitos):
    """Action para tercería tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "TERCERÍA DE PROPIEDAD"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_terceria_tributaria"


class ActionTramitesSuspensionTributaria(BaseTramiteRequisitos):
    """Action para suspensión tributaria"""

    def __init__(self):
        super().__init__()
        self.titulo_tramite = "SUSPENSIÓN DE COBRANZA COACTIVA"
        self.tipo_tramite = "tributarios"

    def name(self) -> Text:
        return "action_tramites_suspension_tributaria"
