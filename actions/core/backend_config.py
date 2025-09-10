"""
Configuración para el backend del sistema de ciudadanos
"""
import os

class BackendConfig:
    """Configuración centralizada para el backend"""

    # URL base del backend - hardcodeada temporalmente
    BASE_URL = "http://localhost:3000"

    # Endpoints de ciudadanos
    CITIZEN_GET_INFO = "/v1/channel-room/citizen/{phone}/basic-information"

    CITIZEN_REQUEST_ADVISOR = "/v1/channel-room/citizen/{phone}/request-advisor"

    CITIZEN_UPDATE = "/v1/channel-room/citizen/basic-information/update"