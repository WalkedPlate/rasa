"""
Actions para trámites administrativos de papeletas
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionTramitesRecursoReconsideracion(Action):
    """Action para recurso de reconsideración de papeletas"""

    def name(self) -> Text:
        return "action_tramites_recurso_reconsideracion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para recurso de reconsideración")

        message = """📋 **REQUISITOS PARA RECURSO DE RECONSIDERACIÓN EN MATERIA DE TRÁNSITO Y TRANSPORTE**

1. **Presentar escrito fundamentado consignando lo siguiente:**
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso.
   b) Domicilio del solicitante.
   c) Expresión concreta de lo pedido, señalando el número del documento impugnado.
   d) Fundamentos de hecho y derecho.
   e) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante de ser caso.

2. **Adjuntar nueva prueba.** En caso no se cumpla con adjuntar nueva prueba o esta no califique como tal, este procedimiento será tramitado como recurso de apelación, de acuerdo a lo señalado en el artículo 213° de la Ley 27444, Ley de Procedimiento Administrativo General.

3. **En caso el trámite fuera presentado por un representante,** adjuntar Carta Poder Simple con firma del administrado o designación de persona cierta debidamente identificada en el escrito.

📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 – 28/08/2018).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesDescargoInfracciones(Action):
    """Action para descarga de infracciones"""

    def name(self) -> Text:
        return "action_tramites_descargo_infracciones"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información para descarga de infracciones")

        message = """📋 **DESCARGA DE INFRACCIONES**

**REQUISITOS PARA RECURSO DE DESCARGO DE INFRACCIONES:**  
1. Presentar solicitud según formato publicado por el SAT conteniendo lo siguiente: 
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso. 
   b) Domicilio del solicitante. 
   c) Expresión concreta de lo pedido, señalando el número del documento impugnado. 
   d) Fundamentos de hecho y de derecho. 
   e) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, de ser el caso.

2. En caso el trámite fuera presentado por un representante, deberá presentar Carta Poder Simple con firma del administrado o designación de persona cierta debidamente identificada en el escrito. 
📋 **Fuente:** Directiva N°  001-006-00000025 Directiva que establece lineamientos para la presentación del trámite de descargo en materia de tránsito y transporte, y de verificación de datos en el Servicio de Administración Tributaria de la Municipalidad Metropolitana de Lima. -  21/12/2017.

**Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesApelacionPapeletas(Action):
    """Action para apelación de papeletas"""

    def name(self) -> Text:
        return "action_tramites_apelacion_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para apelación de papeletas")

        message = """📋 **RECURSO DE APELACIÓN DE PAPELETAS**

**REQUISITOS PARA RECURSO DE APELACIÓN EN MATERIA NO TRIBUTARIA** 
1. Presentar escrito conteniendo lo siguiente: 
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso. 
   b) Domicilio del solicitante. 
   c) Expresión concreta de lo pedido, señalando el número del documento impugnado. 
   d) Fundamentos de hecho y de derecho. 
   e) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, de ser el caso. 

2. En caso el trámite fuera presentado por un representante, deberá presentar Carta Poder Simple con firma del administrado o designación de persona cierta debidamente identificada en el escrito. 
 
📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 28/08/2018).

📋 **Puede ingresar su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

✍️Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.
📌https://casilla.mtc.gob.pe/#/registro

Base Legal: R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesPrescripcionPapeletas(Action):
    """Action para prescripción de papeletas"""

    def name(self) -> Text:
        return "action_tramites_prescripcion_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para prescripción de papeletas")

        message = """📋 **REQUISITOS PARA LA SOLICITUD DE PRESCRIPCIÓN EN MATERIA DE TRÁNSITO, MULTAS DE TRANSPORTE Y MULTAS ADMINISTRATIVAS**

⏰ **El plazo para prescripción de las multas por infracciones al Reglamento Nacional de Tránsito es de dos años computados a partir de la firmeza de la Resolución de Sanción.**

**REQUISITOS:**
1. **Presentar solicitud según formato publicado por el SAT** conteniendo lo siguiente:
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso.
   b) Domicilio del solicitante.
   c) Indicar la obligación cuya prescripción se invoca.
   d) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, de ser el caso.

2. **En caso el trámite fuera presentado por un representante,** deberá presentar Carta Poder Simple con firma del administrado o designación de persona cierta debidamente identificada en el escrito.
📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 28/08/2018).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesDevolucionPapeletas(Action):
    """Action para devolución y/o compensación de papeletas"""

    def name(self) -> Text:
        return "action_tramites_devolucion_papeletas"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para devolución de papeletas")

        message = """📋 **DEVOLUCIÓN Y/O COMPENSACIÓN DE PAPELETAS**


**REQUISITOS PARA LA DEVOLUCIÓN Y/O COMPENSACIÓN EN MATERIA DE MULTAS DE TRÁNSITO, MULTAS DE TRANSPORTE Y MULTAS ADMINISTRATIVAS**
1. Presentar solicitud según formato publicado por el SAT conteniendo lo siguiente: 
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso. 
   b) Domicilio del solicitante. 
   c) Indicar la obligación cuya devolución y/o compensación se solicita. 
   d) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, de ser el caso. 
2. En caso el trámite fuera presentado por un representante, adjuntar documento que acredite la representación. 
 
📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 28/08/2018).

Ingrese su trámite por Mesa de Partes Digital:
📌https://www.sat.gob.pe/MesaPartesDigital

⚠️ **Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.**
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesTerceriaRequisitos(Action):
    """Action para tercería de propiedad (requisitos papeletas)"""

    def name(self) -> Text:
        return "action_tramites_terceria_requisitos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para tercería de propiedad (papeletas)")

        message = """📋 **TERCERÍA DE PROPIEDAD - REQUISITOS ADMINISTRATIVOS**

**REQUISITOS PARA LA SOLICITUD DE TERCERÍA DE PROPIEDAD ANTE COBRANZA DE OBLIGACIONES NO TRIBUTARIAS**
1. Presentar solicitud según formato publicado por el SAT conteniendo lo siguiente: 
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o Número de RUC del solicitante y de su representante, de ser el caso. 
   b) Domicilio del solicitante. 
   c) Indicación del bien afectado. 
   d) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o Representante de ser el caso. 
2. En caso el trámite fuera presentado por un representante, deberá presentar Carta Poder Simple con firma del administrado o designación de persona cierta debidamente identificada en el escrito. 
3. Presentar copia simple del documento privado con fecha cierta, documento público o de otro documento, que acredite fehacientemente la propiedad de los bienes antes de haberse trabado la medida cautelar, acompañada de la declaración jurada del administrado acerca de su autenticidad. 
 
📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 28/08/2018).

📋 **Puede ingresar su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

✍️ Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesSuspensionRequisitos(Action):
    """Action para suspensión de cobranza coactiva (requisitos papeletas)"""

    def name(self) -> Text:
        return "action_tramites_suspension_requisitos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para suspensión de cobranza (papeletas)")

        message = """📋 **SOLICITUD DE SUSPENSIÓN DE COBRANZA COACTIVA - REQUISITOS ADMINISTRATIVOS**

**REQUISITOS PARA LA SUSPENSIÓN DE LA COBRANZA COACTIVA NO TRIBUTARIA**
1. Adjuntar formato de la solicitud de suspensión publicado por el SAT debidamente llenado, por cada papeleta, resolución de sanción o multa administrativa, y por cada una de las causales contempladas en la ley. 
2. Indicar el domicilio real o procesal dentro del radio urbano de la provincia de Lima. 
3. En el caso de representación, presentar poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT. 
4. Argumentar y sustentar su solicitud en virtud del Art. 16 de la Ley de Procedimiento de Ejecución Coactiva (Ley 26979). 
 
📋 **Fuente:** Directiva N° 001-006-00000023 (Resolución Jefatural N° 001-004-00003951 – 18/07/2017).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

✍️ Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.
📌 https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []