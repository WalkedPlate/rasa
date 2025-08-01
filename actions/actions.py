"""
Archivo principal de actions que importa todos los custom actions del chatbot SAT
"""

# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Imports de actions por módulo
from .shared.session_actions import ActionFinalizarChat
from .papeletas.consulta_actions import ActionConsultarPapeletas
from .papeletas.codigo_actions import ActionConsultarCodigoFalta

# Lista de todos los actions disponibles (para referencia)
__all__ = [
    'ActionFinalizarChat',
    'ActionConsultarPapeletas', 
    'ActionConsultarCodigoFalta'
]

# Log de inicialización
logger = logging.getLogger(__name__)
logger.info("📦 Actions del SAT Lima cargados correctamente")
logger.info(f"✅ Actions disponibles: {len(__all__)}")
for action in __all__:
    logger.info(f"   • {action}")

# Mensaje de inicialización
print("=" * 60)
print("🏛️  CHATBOT SAT DE LIMA - ACTIONS INICIALIZADOS")
print("=" * 60)
print(f"📊 Total de custom actions: {len(__all__)}")
print("🚀 Sistema listo para recibir consultas")
print("=" * 60)