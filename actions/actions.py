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

]