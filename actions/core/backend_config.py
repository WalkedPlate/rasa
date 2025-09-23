"""
Configuración para el backend del sistema de ciudadanos
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class BackendConfig:
    """Configuración centralizada para el backend"""

    # URL base del backend desde .env
    BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:3000')

    # Endpoints de ciudadanos desde .env
    CITIZEN_GET_INFO = os.getenv(
        'CITIZEN_GET_INFO_ENDPOINT',
        '/v1/channel-room/citizen/{phone}/basic-information'
    )

    CITIZEN_REQUEST_ADVISOR = os.getenv(
        'CITIZEN_REQUEST_ADVISOR_ENDPOINT',
        '/v1/channel-room/citizen/{phone}/request-advisor'
    )

    CITIZEN_UPDATE = os.getenv(
        'CITIZEN_UPDATE_ENDPOINT',
        '/v1/channel-room/citizen/basic-information/update'
    )

    ASSISTANCE_CLOSE = os.getenv(
        'ASSISTANCE_CLOSE_ENDPOINT',
        '/v1/channel-room/assistances/close'
    )