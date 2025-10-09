# ============================================================================
# IMPORTS - HANDLERS COMPARTIDOS (Shared)
# ============================================================================
from actions.handlers.shared.session_actions import ActionFinalizarChat
from actions.handlers.shared.advisor_actions import ActionSolicitarAsesor
from actions.handlers.shared.fallback_actions import (
    ActionSmartFallback,
    ActionResetFallbackCount
)
from actions.handlers.shared.router_actions import ActionRouteDocumentConsultation

# ============================================================================
# IMPORTS - HANDLERS DE PAPELETAS
# ============================================================================
from actions.handlers.papeletas.consulta_actions import ActionConsultarPapeletas
from actions.handlers.papeletas.codigo_actions import ActionConsultarCodigoFalta

# ============================================================================
# IMPORTS - HANDLERS DE IMPUESTOS
# ============================================================================
from actions.handlers.impuestos.consulta_actions import ActionConsultarImpuestos
from actions.handlers.impuestos.cuadernillo_actions import (
    ActionCuadernilloAgenciaVirtual,
)
from actions.handlers.impuestos.declaracion_actions import (
    ActionDeclaracionImpuestoVehicular,
    ActionLiquidacionAlcabala,
    ActionDeclaracionImpuestoPredial,
    ActionFraccionarDeuda
)
from actions.handlers.impuestos.beneficios_actions import (
    ActionBeneficiosPensionista,
    ActionBeneficiosAdultoMayor
)

# ============================================================================
# IMPORTS - HANDLERS DE RETENCIÓN Y CAPTURA
# ============================================================================
from actions.handlers.retencion.consulta_actions import ActionConsultarOrdenCaptura
from actions.handlers.retencion.tramites_actions import (
    ActionRetencionEmbargo,
    ActionRetencionVehiculoInternado,
    ActionRetencionSuspenderCobranza,
    ActionRetencionTerceriaPropiedad,
    ActionRetencionRemateVehicular
)

# ============================================================================
# IMPORTS - HANDLERS DE LUGARES Y PAGOS
# ============================================================================
from actions.handlers.lugares_pagos.informacion_actions import (
    ActionLugaresAgenciasHorarios,
    ActionLugaresPago,
    ActionLugaresFormasPago
)

# ============================================================================
# IMPORTS - HANDLERS DE SERVICIOS VIRTUALES
# ============================================================================
from actions.handlers.servicios_virtuales.servicios_actions import (
    ActionServiciosMesaPartes,
    ActionServiciosAgenciaVirtual,
    ActionServiciosPitazo,
    ActionServiciosCorreo,
    ActionServiciosLibroReclamaciones,
    ActionServiciosCursos
)

# ============================================================================
# IMPORTS - HANDLERS DE TRÁMITES
# ============================================================================
from actions.handlers.tramites.consulta_actions import ActionConsultarTramite
from actions.handlers.tramites.generales_actions import (
    ActionTramitesConstanciasNoAdeudo
)
from actions.handlers.tramites.papeletas_tramites_actions import (
    ActionTramitesRecursoReconsideracion,
    ActionTramitesApelacionPapeletas,
    ActionTramitesPrescripcionPapeletas,
    ActionTramitesDevolucionPapeletas,
    ActionTramitesTerceriaRequisitos,
    ActionTramitesSuspensionRequisitos
)
from actions.handlers.tramites.tributarios_tramites_actions import (
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

# ============================================================================
# EXPORTACIÓN DE TODAS LAS ACTIONS
# ============================================================================
__all__ = [
    # ========================================================================
    # SHARED - Actions compartidos
    # ========================================================================
    'ActionFinalizarChat',
    'ActionSolicitarAsesor',
    'ActionSmartFallback',
    'ActionResetFallbackCount',
    'ActionRouteDocumentConsultation',

    # ========================================================================
    # PAPELETAS - Consultas de multas e infracciones
    # ========================================================================
    'ActionConsultarPapeletas',
    'ActionConsultarCodigoFalta',

    # ========================================================================
    # IMPUESTOS - Deuda tributaria y declaraciones
    # ========================================================================
    'ActionConsultarImpuestos',
    'ActionCuadernilloAgenciaVirtual',
    'ActionDeclaracionImpuestoVehicular',
    'ActionLiquidacionAlcabala',
    'ActionDeclaracionImpuestoPredial',
    'ActionFraccionarDeuda',
    'ActionBeneficiosPensionista',
    'ActionBeneficiosAdultoMayor',

    # ========================================================================
    # RETENCIÓN - Órdenes de captura y medidas cautelares
    # ========================================================================
    'ActionConsultarOrdenCaptura',
    'ActionRetencionEmbargo',
    'ActionRetencionVehiculoInternado',
    'ActionRetencionSuspenderCobranza',
    'ActionRetencionTerceriaPropiedad',
    'ActionRetencionRemateVehicular',

    # ========================================================================
    # LUGARES Y PAGOS - Información presencial y pagos
    # ========================================================================
    'ActionLugaresAgenciasHorarios',
    'ActionLugaresPago',
    'ActionLugaresFormasPago',

    # ========================================================================
    # SERVICIOS VIRTUALES - Servicios digitales del SAT
    # ========================================================================
    'ActionServiciosMesaPartes',
    'ActionServiciosAgenciaVirtual',
    'ActionServiciosPitazo',
    'ActionServiciosCorreo',
    'ActionServiciosLibroReclamaciones',
    'ActionServiciosCursos',

    # ========================================================================
    # TRÁMITES - Trámites administrativos y requisitos
    # ========================================================================
    'ActionConsultarTramite',
    'ActionTramitesConstanciasNoAdeudo',

    # Trámites de papeletas
    'ActionTramitesRecursoReconsideracion',
    'ActionTramitesApelacionPapeletas',
    'ActionTramitesPrescripcionPapeletas',
    'ActionTramitesDevolucionPapeletas',
    'ActionTramitesTerceriaRequisitos',
    'ActionTramitesSuspensionRequisitos',

    # Trámites tributarios
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