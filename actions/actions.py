# Imports de actions
from .shared.fallback_actions import ActionResetFallbackCount, ActionSmartFallback
from .shared.session_actions import ActionFinalizarChat
from .shared.advisor_actions import ActionSolicitarAsesor
from .papeletas.consulta_actions import ActionConsultarPapeletas
from .papeletas.codigo_actions import ActionConsultarCodigoFalta
from .impuestos.consulta_actions import ActionConsultarImpuestos

# Imports de actions de impuestos
from .impuestos.cuadernillo_actions import (
    ActionCuadernilloAgenciaVirtual,
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
    ActionRetencionRemateVehicular
)
# Imports de actions de actualizar datos
from .actualizar.datos_actions import (
    ActionActualizarDatos,
    ActionActualizarNombre,
    ActionProcesarNuevoNombre,
    ActionActualizarDocumento,
    ActionProcesarTipoDocumento,
    ActionProcesarNumeroDocumento
)

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

# Imports de actions de trámites
from .tramites.consulta_actions import ActionConsultarTramite
from .tramites.generales_actions import (
    ActionTramitesConstanciasNoAdeudo
)
from .tramites.papeletas_tramites_actions import (
    ActionTramitesRecursoReconsideracion,
    ActionTramitesDescargoInfracciones,
    ActionTramitesApelacionPapeletas,
    ActionTramitesPrescripcionPapeletas,
    ActionTramitesDevolucionPapeletas,
    ActionTramitesTerceriaRequisitos,
    ActionTramitesSuspensionRequisitos
)

from .tramites.tributarios_tramites_actions import (
    ActionTramitesPredialRequisitos,
    ActionTramitesVehicularRequisitos,
    ActionTramitesAlcabalaRequisitos,
    ActionTramitesReclamacionTributaria,
    ActionTramitesPrescripcionTributaria,
    ActionTramitesDevolucionTributaria,
    ActionTramitesApelacionTributaria,
    ActionTramitesTerceriaTributaria,
    ActionTramitesSuspensionTributaria
)
from .shared.router_actions import ActionRouteDocumentConsultation

# Lista de todos los actions disponibles
__all__ = [
    # Actions básicos
    'ActionFinalizarChat',
    'ActionSolicitarAsesor',
    'ActionSmartFallback',
    'ActionResetFallbackCount',

    # Actions de papeletas
    'ActionConsultarPapeletas',
    'ActionConsultarCodigoFalta',
    
    # Actions de impuestos
    'ActionConsultarImpuestos',
    'ActionCuadernilloAgenciaVirtual',
    'ActionDeclaracionImpuestoVehicular',
    'ActionLiquidacionAlcabala',
    'ActionDeclaracionImpuestoPredial',
    'ActionFraccionarDeuda',
    'ActionBeneficiosPensionista',
    'ActionBeneficiosAdultoMayor',
    'ActionRouteDocumentConsultation',

    # Actions de retención
    'ActionConsultarOrdenCaptura',
    'ActionRetencionEmbargo',
    'ActionRetencionVehiculoInternado',
    'ActionRetencionSuspenderCobranza',
    'ActionRetencionTerceriaPropiedad',
    'ActionRetencionRemateVehicular',

    # Actions de actualizar datos
    'ActionActualizarDatos',
    'ActionActualizarNombre',
    'ActionProcesarNuevoNombre',
    'ActionActualizarDocumento',
    'ActionProcesarTipoDocumento',
    'ActionProcesarNumeroDocumento',

    # Actions de lugares y pagos
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

    # Actions de trámites
    'ActionConsultarTramite',
    'ActionTramitesConstanciasNoAdeudo',
    'ActionTramitesRecursoReconsideracion',
    'ActionTramitesApelacionPapeletas',
    'ActionTramitesPrescripcionPapeletas',
    'ActionTramitesDevolucionPapeletas',
    'ActionTramitesTerceriaRequisitos',
    'ActionTramitesSuspensionRequisitos',
    'ActionTramitesPredialRequisitos',
    'ActionTramitesVehicularRequisitos',
    'ActionTramitesAlcabalaRequisitos',
    'ActionTramitesReclamacionTributaria',
    'ActionTramitesPrescripcionTributaria',
    'ActionTramitesDevolucionTributaria',
    'ActionTramitesApelacionTributaria',
    'ActionTramitesTerceriaTributaria',
    'ActionTramitesSuspensionTributaria',


]