"""
Archivo principal de actions del chatbot SAT de Lima
"""

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Imports de actions simplificados
from .shared.session_actions import ActionFinalizarChat
from .papeletas.consulta_actions import ActionConsultarPapeletas
from .papeletas.codigo_actions import ActionConsultarCodigoFalta

# Lista de todos los actions disponibles
__all__ = [
    'ActionFinalizarChat',
    'ActionConsultarPapeletas',
    'ActionConsultarCodigoFalta'
]

# Log de inicialización
logger = logging.getLogger(__name__)
logger.info("Actions del SAT Lima cargados - Versión simplificada")
logger.info(f"Actions disponibles: {len(__all__)}")
for action in __all__:
    logger.info(f"  • {action}")

print("=" * 60)
print("CHATBOT SAT DE LIMA - ACTIONS SIMPLIFICADOS")
print("=" * 60)
print(f"Total de custom actions: {len(__all__)}")
print("Características:")
print("  • Sin confirmaciones complejas")
print("  • Consultas API directas")
print("  • Navegación fluida")
print("  • Respuestas contextuales")
print("Sistema listo para recibir consultas")
print("=" * 60)