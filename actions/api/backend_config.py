"""
Configuración para el backend del sistema de ciudadanos
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class BackendConfig:
    """Configuración centralizada para el backend"""

    # URL base del backend
    BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:3000')

    # Credenciales de autenticación
    AUTH_EMAIL = os.getenv('BACKEND_AUTH_EMAIL', 'rasa-bot@mail.com')
    AUTH_PASSWORD = os.getenv('BACKEND_AUTH_PASSWORD', 'QiMAL5JDP8sfzfom')

    # Endpoints de autenticación
    AUTH_LOGIN_ENDPOINT = os.getenv(
        'BACKEND_AUTH_LOGIN_ENDPOINT',
        '/v1/auth/login'
    )

    # Endpoints de ciudadanos
    CITIZEN_GET_INFO = os.getenv(
        'CITIZEN_GET_INFO_ENDPOINT',
        '/v1/channel-citizen/{phone}/basic-information'
    )

    CITIZEN_REQUEST_ADVISOR = os.getenv(
        'CITIZEN_REQUEST_ADVISOR_ENDPOINT',
        '/v1/channel-citizen/{phone}/request-advisor'
    )

    ASSISTANCE_CLOSE = os.getenv(
        'ASSISTANCE_CLOSE_ENDPOINT',
        '/v1/channel-room/assistances/assistance/close'
    )

    BOT_QUERY_LOG = os.getenv(
        'BOT_QUERY_LOG_ENDPOINT',
        '/v1/channel-room/citizen/{phone}/bot-query'
    )


    FAREWELL_MESSAGES = os.getenv(
        'FAREWELL_MESSAGES_ENDPOINT',
        '/v1/automatic-messages/farewell-by-channel/{categoryId}'
    )

    # Category ID para el canal (por defecto 4)
    CHANNEL_CATEGORY_ID = int(os.getenv('CHANNEL_CATEGORY_ID', '4'))