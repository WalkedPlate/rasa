"""
Actions para trámites administrativos tributarios
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)


class ActionTramitesPredialRequisitos(Action):
    """Action para requisitos de declaración predial"""

    def name(self) -> Text:
        return "action_tramites_predial_requisitos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos administrativos para declaración predial")

        message = """📋 **REQUISITOS PARA LA DECLARACIÓN DE IMPUESTO PREDIAL**

**INSCRIPCIÓN:**
1. **Exhibir el documento de identidad** del propietario o de su representante, de ser el caso.
2. **Exhibir el último recibo** de alguno de los servicios (luz, agua, teléfono, etc.) del domicilio del propietario.
3. **En el caso de representación,** presentar poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT.
4. **Exhibir el original y presentar copia simple** del documento que sustente la adquisición:
   - **Compra/Venta/Permuta/Adjudicación:** Contrato
   - **Donación/Anticipo de Legítima:** Escritura pública
   - **Herencia/Sucesión:** Partida de defunción, declaratoria de herederos, testamento, sentencia o escritura pública que señala la división y partición de los bienes
   - **Remate:** Resolución Judicial o Administrativa mediante la cual se adjudica el bien, debidamente consentida
   - **Fusión:** Copia literal de la inscripción en Registros Públicos donde conste la fecha de vigencia del acuerdo de fusión
   - **Escisión:** Copia literal de la inscripción en Registros Públicos donde conste la fecha de vigencia del acuerdo de Escisión
   - **En los demás casos:** documento que acredite la propiedad

**RECTIFICACIÓN (*):**
- Exhibir el documento de identidad del propietario o de su representante, de ser el caso
- En caso de representación, presentar poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT
- Exhibir original y presentar copia simple de los documentos sustentatorios de la rectificación realizada

📋 **Fuente:** Directiva N° 001-006-00000023 (Resolución Jefatural N° 001-004-00003951 – 18/07/2017) 
(*) Consultar requisitos establecido en el TUSNE del SAT de Lima

**Puede presentar su declaración por Agencia Virtual SAT:**
📌 https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesVehicularRequisitos(Action):
    """Action para requisitos de declaración vehicular"""

    def name(self) -> Text:
        return "action_tramites_vehicular_requisitos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos administrativos para declaración vehicular")

        message = """📋 **DECLARACIÓN DE IMPUESTO VEHICULAR - REQUISITOS ADMINISTRATIVOS**

**REQUISITOS PARA LA DECLARACIÓN DEL IMPUESTO VEHICULAR**
**Inscripción**
1. Exhibir el documento de identidad del propietario o de su representante, de ser el caso. 
2. Exhibir el último recibo de servicios (luz, agua, teléfono, etc.) del domicilio del propietario. 
3. En el caso de representación, presentar poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT. 
4. Tarjeta de identificación vehicular. 
5. Exhibir el original y presentar copia simple del documento que sustente la adquisición: 
-  Copia de factura, boleta de venta, acta de transferencia o declaración única de aduanas (DUA o póliza de importación). 
-  Otras transferencias: 
-  Compra / Venta / Permuta / Adjudicación: Contrato 
-  Donación / Anticipo de Legítima: Escritura pública. 
-  Remate: Resolución Judicial o Administrativa mediante la cual se adjudica el bien, debidamente consentida. 
-  Otros casos: revisar www.sat.gob.pe 
-  En caso de rectificación exhibir original y presentar copia simple de los documentos sustentatorios de la rectificación realizada. 
**En caso de robo**
-  Exhibir el documento de identidad del propietario o de su representante, de ser el caso. 
-  Presentar original o copia certificada de la denuncia policial del hurto o robo del vehículo. 
-  Presentar copia de la anotación del hurto o robo en la partida registral del vehículo. 
 
Fuente: Directiva N° 001-006-00000023 (Resolución Jefatural N° 001-004-00003951 – 18/07/2017).

**Puede presentar su declaración por Agencia Virtual SAT:**
🔗 **Para registrarse:**
📌 https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesAlcabalaRequisitos(Action):
    """Action para requisitos de liquidación de alcabala"""

    def name(self) -> Text:
        return "action_tramites_alcabala_requisitos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos administrativos para liquidación de alcabala")

        message = """📋 **REQUISITOS PARA LA LIQUIDACIÓN DE ALCABALA**

1. **Exhibir el documento de identidad** de la persona que realiza el trámite
2. **Presentar copia simple** del documento en el que consta la transferencia de propiedad
3. **Presentar copia simple del autovalúo** del año en que se produjo la transferencia (en caso que el predio no esté ubicado en el Cercado ni inscrito en el SAT)
4. **En el caso de primera venta efectuada por:**
   a) **Empresa constructora:** presentar Ficha RUC donde señale que su actividad económica es la construcción de edificios completos o construcción de inmuebles, o presentar copia simple de constitución de persona jurídica cuyo objeto social señale la construcción de inmuebles
   b) **Personas que no realicen actividad empresarial de construcción:** acreditar por lo menos 2 ventas en los últimos 12 meses (sin incluir la venta materia de liquidación)
5. **Cuando se trate de bienes futuros:** presentar copia simple del certificado de conformidad de obra o documento que acredite la existencia del bien (Acta de entrega/Partida de Independización)

📋 **Fuente:** Directiva N° 001-006-00000023 (Resolución Jefatural N° 001-004-00003951 – 18/07/2017).

**Puede presentar su declaración por Agencia Virtual SAT:**
📌 https://www.sat.gob.pe/websitev9/Servicios/AgenciaVirtual

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesReclamacionTributaria(Action):
    """Action para recurso de reclamación tributaria"""

    def name(self) -> Text:
        return "action_tramites_reclamacion_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para recurso de reclamación tributaria")

        message = """📋 **REQUISITOS PARA PRESENTACIÓN DE RECURSO DE RECLAMACIÓN EN MATERIA TRIBUTARIA**

1. **Presentar escrito fundamentado** consignando lo siguiente:
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso
   b) Domicilio del solicitante
   c) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, según corresponda

2. **En caso el trámite fuera presentado por un representante,** deberá presentar poder especial en documento público o privado con firma legalizada notarialmente o certificada por fedatario del SAT

3. **En caso de reclamación parcial** contra resolución de determinación y de multa, efectuar el pago de la parte no reclamada actualizada hasta la fecha en que se realice el pago

4. **En caso de reclamación contra orden de pago,** efectuar el pago de la deuda reclamada, actualizada

5. **En caso de reclamación extemporánea** de la Resolución de Determinación o de Multa, efectuar el pago de la totalidad de la deuda que se reclama, actualizada hasta la fecha de pago o presentar carta fianza bancaria o financiera por el monto de la deuda actualizada hasta por nueve (09) meses posteriores a la fecha de interposición del recurso, con una vigencia de nueve (9) meses, debiendo renovarse por períodos similares dentro del plazo que señale la Administración

6. **En caso de reclamación contra la denegatoria** de la solicitud de devolución, indicar número de resolución denegatoria

7. **En caso de reclamación contra la denegatoria ficta** de solicitud no contenciosa, indicar el número de expediente de presentación de la solicitud

8. **En caso de reclamación contra la Resolución** que declara la pérdida del fraccionamiento deberá indicar número de la resolución de pérdida

📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 – 28/08/2018).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesPrescripcionTributaria(Action):
    """Action para prescripción tributaria"""

    def name(self) -> Text:
        return "action_tramites_prescripcion_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para prescripción tributaria")

        message = """📋 **REQUISITOS PARA SOLICITUD DE PRESCRIPCIÓN EN MATERIA TRIBUTARIA**

1. **Presentar solicitud** según formato publicado por el SAT conteniendo lo siguiente:
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso
   b) Domicilio del solicitante
   c) Indicar la obligación tributaria cuya prescripción se requiere
   d) Firma o huella digital (en caso de no saber firmar o estar impedido), del solicitante o representante, según corresponda

2. **En caso el trámite fuera presentado por un representante,** adjuntar documento que acredite la representación

📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 – 28/08/2018).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesDevolucionTributaria(Action):
    """Action para devolución tributaria"""

    def name(self) -> Text:
        return "action_tramites_devolucion_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para devolución tributaria")

        message = """📋 **REQUISITOS PARA SOLICITUD DE COMPENSACIÓN Y/U DEVOLUCIÓN EN MATERIA TRIBUTARIA**

1. **Presentar solicitud** según formato publicado por el SAT conteniendo lo siguiente:
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso
   b) Domicilio del solicitante
   c) Indicar la deuda tributaria a compensar, la misma que debe ser exigible (*)
   d) Firma o huella digital (en caso de no saber firmar o estar impedido), del solicitante o representante, de ser el caso

2. **En caso el trámite fuera presentado por un representante,** deberá presentar poder especial en documento público o privado con firma legalizada notarialmente o certificada por fedatario del SAT

(**) A fin de facilitar la diligencia de su trámite sírvase adjuntar, en original o copia autenticada el recibo de pago de la deuda señalada.

📋 **Fuente:** TUPA - SAT de Lima (Decreto de Alcaldía N° 0008 del 28/08/2018).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesApelacionTributaria(Action):
    """Action para apelación tributaria"""

    def name(self) -> Text:
        return "action_tramites_apelacion_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para apelación tributaria")

        message = """📋 **RECURSO DE APELACIÓN TRIBUTARIA**

**REQUISITOS PARA EL RECURSO DE APELACIÓN EN MATERIA TRIBUTARIA**
1. Presentar escrito conteniendo lo siguiente: 
   a) Nombres y apellidos o denominación o razón social, número de documento de identidad o número de RUC del solicitante y de su representante, de ser el caso. 
   b) Domicilio del solicitante. 
   c) Expresión concreta de lo pedido, señalando el número del documento impugnado. 
   d) Fundamentos de hecho y de derecho 
   e) Firma o huella digital (en caso de no saber firmar o estar impedido) del solicitante o representante, de ser el caso. 
2. En caso el trámite fuera presentado por un representante, deberá presentar Poder especial en documento público o privado con firma legalizada notarialmente o certificada por fedatario del SAT. 
 
📋 **Fuente:** Artículos 143 del TUO del Código Tributario Decreto Supremo N.° 135-99-EF y modificatorias.

📋 **Puede ingresar su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesTerceriaTributaria(Action):
    """Action para tercería tributaria"""

    def name(self) -> Text:
        return "action_tramites_terceria_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para tercería tributaria")

        message = """📋 **TERCERÍA DE PROPIEDAD TRIBUTARIA**

Para verificar los requisitos detallados:

🔗 **Requisitos completos:**
📌 https://www.sat.gob.pe/WebSiteV9/Tramites/TramitesTUPA/TUPA

📋 **Descargue y consulte el llenado del formato:**
📌 https://www.sat.gob.pe/WebSiteV8/Modulos/Tramites/TramitesAdministv2.aspx

📋 **Puede ingresar su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Requisitos tributarios' - Ver otros trámites tributarios
• 'Otros trámites' - Volver al menú principal de trámites
• 'Menú principal' - Otras opciones"""

        dispatcher.utter_message(text=message)
        return []


class ActionTramitesSuspensionTributaria(Action):
    """Action para suspensión tributaria"""

    def name(self) -> Text:
        return "action_tramites_suspension_tributaria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info("Mostrando requisitos para suspensión tributaria")

        message = """📋 **REQUISITOS PARA SOLICITUD DE SUSPENSIÓN DE COBRANZA COACTIVA DE OBLIGACIONES TRIBUTARIAS**

REQUISITOS PARA SOLICITUD DE SUSPENSIÓN DE COBRANZA COACTIVA DE OBLIGACIONES TRIBUTARIAS 
1. Formato de solicitud de suspensión proporcionado por el SAT debidamente llenado y firmado por el solicitante o representante legal. 
2. Indicar el domicilio real o procesal dentro del radio urbano de la provincia de Lima. 
3. En caso de representación, presentar poder específico en documento público o privado con firma legalizada ante notario o certificada por fedatario del SAT. 
4. Argumentar y sustentar su solicitud en virtud del Art. 16 de la Ley de Procedimiento de Ejecución Coactiva (Ley 26979). 
5. En caso de cobranza dirigida contra persona distinta al obligado, acreditar que no es el obligado con documento de fecha cierta. 
6. En caso de recurso administrativo presentado dentro del plazo de ley: señalar número de expediente y fecha de presentación. En caso de tratarse de recursos presentados ante órganos distintos al SAT, presentar copia simple del cargo de presentación del mismo con sello de recepción. 
7. De encontrase sometido a un procedimiento concursal deberá presentar lo siguiente: 
   a) Presentar la publicación de la declaración de insolvencia. 
   b) Presentar copia simple del plan de Reestructuración o del Acuerdo Global de Financiamiento. 
   c) El administrado o un tercero podrá comunicar el estado de quiebra presentando copia simple de la Resolución de Quiebra Judicial (Puede ser judicial o extrajudicial). 
8. En caso de Disolución y Liquidación de un administrado bajo supervisión de la SBS, deberá cumplir con lo siguiente: 
   a) Señalar fecha de publicación de la Resolución de Disolución y Liquidación emitida por la SBS. 
   b) Adjuntar copia de la publicación en el diario. 
9. En caso de empresas estatales comprendidas en los supuestos del Decreto Ley N° 25604 debe presentarse la decisión o acuerdo PROINVERSIÓN en que se especifique la modalidad de promoción de inversión privada y la intangibilidad de los bienes de la empresa. 
10. En caso de demanda de amparo o demanda contenciosa administrativa, adjuntar copia certificada por el auxiliar jurisdiccional de la resolución favorable al administrado. 
11. En caso de Revisión Judicial, adjuntar copia de la demanda con el sello de recepción del Poder Judicial.  
 
📋 **Fuente:** Directiva N° 001-006-00000023 (Resolución Jefatural N° 001-004-00003951 – 18/07/2017).

📋 **Ingrese su trámite por Mesa de Partes Digital:**
📌 https://www.sat.gob.pe/MesaPartesDigital

**¿Qué más necesitas?**
• 'Menú principal' - Otras opciones
• 'Finalizar chat'
"""

        dispatcher.utter_message(text=message)
        return []