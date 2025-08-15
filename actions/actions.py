# Imports de actions
from .shared.session_actions import ActionFinalizarChat
from .papeletas.consulta_actions import ActionConsultarPapeletas
from .papeletas.codigo_actions import ActionConsultarCodigoFalta
from .impuestos.consulta_actions import ActionConsultarImpuestos
from .impuestos.cuadernillo_actions import (
    ActionCuadernilloAgenciaVirtual,
    ActionCuadernilloPredial,
    ActionCuadernilloVehicular
)
from .impuestos.declaracion_actions import (
    ActionDeclaracionImpuestoVehicular,
    ActionLiquidacionAlcabala,
    ActionDeclaracionImpuestoPredial,
    ActionFraccionarDeuda
)
from .impuestos.beneficios_actions import (
    ActionBeneficiosPensionista,
    ActionBeneficiosAdultoMayor
)

# Imports de actions de retención
from .retencion.consulta_actions import ActionConsultarOrdenCaptura
from .retencion.tramites_actions import (
    ActionRetencionEmbargo,
    ActionRetencionVehiculoInternado,
    ActionRetencionSuspenderCobranza,
    ActionRetencionTerceriaPropiedad,
    ActionRetencionLevantamiento,
    ActionRetencionRemateVehicular
)
# Imports de actions de actualizar datos
from .actualizar.datos_actions import ActionActualizarDatos

# Imports de actions de lugares y pagos
from .lugares_pagos.informacion_actions import (
    ActionLugaresAgenciasHorarios,
    ActionLugaresPago,
    ActionLugaresFormasPago
)

# Imports de actions de servicios virtuales
from .servicios_virtuales.servicios_actions import (
    ActionServiciosMesaPartes,
    ActionServiciosAgenciaVirtual,
    ActionServiciosPitazo,
    ActionServiciosCorreo,
    ActionServiciosLibroReclamaciones,
    ActionServiciosCursos
)

from .shared.router_actions import ActionRouteDocumentConsultation

# Lista de todos los actions disponibles
__all__ = [
    # Actions existentes
    'ActionFinalizarChat',
    'ActionConsultarPapeletas',
    'ActionConsultarCodigoFalta',
    
    # Actions de impuestos
    'ActionConsultarImpuestos',
    'ActionCuadernilloAgenciaVirtual',
    'ActionCuadernilloPredial', 
    'ActionCuadernilloVehicular',
    'ActionDeclaracionImpuestoVehicular',
    'ActionLiquidacionAlcabala',
    'ActionDeclaracionImpuestoPredial',
    'ActionFraccionarDeuda',
    'ActionBeneficiosPensionista',
    'ActionBeneficiosAdultoMayor',
    'ActionRouteDocumentConsultation'
    

    # Actions de retención
    'ActionConsultarOrdenCaptura',
    'ActionRetencionEmbargo',
    'ActionRetencionVehiculoInternado',
    'ActionRetencionSuspenderCobranza',
    'ActionRetencionTerceriaPropiedad',
    'ActionRetencionLevantamiento',
    'ActionRetencionRemateVehicular',

    # Actions de actualizar datos
    'ActionActualizarDatos',

    # Actions de lugares y pagos (los no repetidos)
    'ActionLugaresAgenciasHorarios',
    'ActionLugaresPago',
    'ActionLugaresFormasPago',

    # Actions de servicios virtuales
    'ActionServiciosMesaPartes',
    'ActionServiciosAgenciaVirtual',
    'ActionServiciosPitazo',
    'ActionServiciosCorreo',
    'ActionServiciosLibroReclamaciones',
    'ActionServiciosCursos',

]