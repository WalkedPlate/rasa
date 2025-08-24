"""
Actions para servicios virtuales del SAT (respuestas simples)
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionServiciosMesaPartes(Action):
    """Action para Mesa de Partes Digital"""

    def name(self) -> Text:
        return "action_servicios_mesa_partes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de Mesa de Partes Digital")

        message = """📄 **MESA DE PARTES DIGITAL**

Puede acceder por nuestra página web a Mesa de Partes Digital para la presentación de sus trámites:

🔗 **Mesa de Partes Digital:**
https://www.sat.gob.pe/MesaPartesDigital

⚠️ **IMPORTANTE - Requisito obligatorio:**
Para iniciar un procedimiento administrativo vinculado a tránsito o transporte, es obligatorio inscribirse en la Casilla Electrónica del MTC, así recibirás oportunamente nuestras comunicaciones.

🔗 **Casilla Electrónica MTC:**
https://casilla.mtc.gob.pe/#/registro

📋 **Base Legal:** R. Directoral N°023-2024-MTC/18

**¿Qué más necesitas?**
• 'Agencia Virtual' - Acceso a servicios online
• 'Casilla MTC' - Información del registro obligatorio
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionServiciosAgenciaVirtual(Action):
    """Action para Agencia Virtual SAT"""

    def name(self) -> Text:
        return "action_servicios_agencia_virtual"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de Agencia Virtual SAT")

        message = """💻 **AGENCIA VIRTUAL SAT**

Para ingresar a nuestra Agencia Virtual SAT, puede registrarse en el siguiente enlace:

🔗 **Registro Agencia Virtual:**
https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

📖 **Guía interactiva:**
Para que pueda guiarse del procedimiento de agencia virtual:
https://www.sat.gob.pe/AgenciaVirtual/guiainteractiva/

**¿Qué más necesitas?**
• 'Mesa de partes' - Presentar trámites administrativos
• 'Facilidades de pago' - Información sobre cuotas
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionServiciosPitazo(Action):
    """Action para suscripción a Pitazo informativo"""

    def name(self) -> Text:
        return "action_servicios_pitazo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de suscripción a Pitazo")

        message = """📢 **SUSCRÍBETE A PITAZO INFORMATIVO**

Recibe alertas automáticas sobre papeletas y notificaciones importantes del SAT.

🔗 **Registro a Pitazo:**
https://www.sat.gob.pe/VirtualSAT/modulos/pitazo/Default.aspx

**¿Qué incluye el servicio Pitazo?**

**¿Qué más necesitas?**
• 'Actualizar datos' - Cambiar tu información de contacto
• 'Consultar papeletas' - Ver tus multas pendientes
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionServiciosCorreo(Action):
    """Action para contacto por correo electrónico"""

    def name(self) -> Text:
        return "action_servicios_correo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de contacto por correo")

        message = """📧 **ENVÍANOS UN CORREO**

Puede dejarnos su consulta al correo oficial del SAT:

📧 **Correo oficial:** asuservicio@sat.gob.pe

🔗 **Formulario web:**
https://www.sat.gob.pe/websitev9/CanalesAtencion/Correo-SAT

**¿Qué más necesitas?**
• 'Oficinas SAT' - Atención presencial
• 'Teléfonos de contacto' - Atención inmediata
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionServiciosLibroReclamaciones(Action):
    """Action para libro de reclamaciones"""

    def name(self) -> Text:
        return "action_servicios_libro_reclamaciones"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información del libro de reclamaciones")

        message = """📝 **LIBRO DE RECLAMACIONES**

Puede ingresar su reclamo de manera oficial y formal:

🔗 **Libro de Reclamaciones Online:**
https://www.sat.gob.pe/websitev9/Servicios/Defensoria/LibroReclamaciones

**¿Qué más necesitas?**
• 'Enviar correo' - Consultas menos formales
• 'Defensoría del usuario' - Más información sobre tus derechos
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionServiciosCursos(Action):
    """Action para cursos del SAT"""

    def name(self) -> Text:
        return "action_servicios_cursos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando información de cursos SAT")

        message = """🎓 **CURSOS SAT**

El SAT de Lima le brinda cursos y capacitaciones especializadas:

🔗 **Escuela SAT:**
https://escuelasat.edu.pe/cursos/

**Cursos disponibles:**
• Tributación municipal
• Administración tributaria
• Procedimientos administrativos
• Cobranza coactiva
• Fiscalización tributaria
• Atención al ciudadano

**Modalidades:**
• Cursos presenciales
• Capacitación virtual
• Seminarios especializados
• Talleres prácticos
• Diplomados

**Dirigido a:**
• Funcionarios públicos
• Profesionales del sector privado
• Estudiantes universitarios
• Ciudadanos interesados en tributación
• Personal administrativo

**Beneficios:**
• Certificación oficial del SAT
• Actualización en normativa tributaria
• Networking profesional
• Metodología práctica
• Docentes especializados

**Información adicional:**
• Costos y becas disponibles
• Cronograma de cursos
• Requisitos de inscripción
• Certificaciones obtenibles

**¿Qué más necesitas?**
• 'Agencia Virtual' - Servicios online del SAT
• 'Mesa de partes' - Presentar trámites
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []