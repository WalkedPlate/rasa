"""
Manejo de autenticación con el backend
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional
from .backend_config import BackendConfig

logger = logging.getLogger(__name__)


class BackendAuthManager:
    """Maneja la autenticación JWT con el backend"""

    def __init__(self):
        self.access_token = None
        self.token_expiry = None
        self.auth_url = f"{BackendConfig.BASE_URL}{BackendConfig.AUTH_LOGIN_ENDPOINT}"
        self.credentials = {
            "email": BackendConfig.AUTH_EMAIL,
            "password": BackendConfig.AUTH_PASSWORD,
            "rememberMe": False  # Token válido por 1 día
        }

    def get_valid_token(self) -> Optional[str]:
        """Obtiene un token válido, renovándolo si es necesario"""
        if self.access_token is None or self.is_token_expired():
            self.refresh_token()
        return self.access_token

    def is_token_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        if self.token_expiry is None:
            return True
        # Renovar 5 minutos antes de expirar
        return datetime.now() >= (self.token_expiry - timedelta(minutes=5))

    def refresh_token(self) -> bool:
        """Obtiene un nuevo token de autenticación"""
        try:
            logger.info("🔐 Renovando token de autenticación del backend...")

            response = requests.post(
                self.auth_url,
                json=self.credentials,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.access_token = data.get("accessToken")

                # Calcular expiración (1 día si rememberMe=False)
                expires_in_hours = 24 if not self.credentials["rememberMe"] else 24 * 30
                self.token_expiry = datetime.now() + timedelta(hours=expires_in_hours)

                logger.info(f"Token renovado exitosamente, expira en {expires_in_hours} horas")
                return True
            else:
                logger.error(f"Error obteniendo token: {response.status_code} - {response.text}")
                self.access_token = None
                return False

        except requests.exceptions.Timeout:
            logger.error("⏱Timeout en autenticación del backend")
            self.access_token = None
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión en autenticación del backend")
            self.access_token = None
            return False
        except Exception as e:
            logger.error(f"Error inesperado en autenticación: {e}")
            self.access_token = None
            return False

    def clear_token(self):
        """Limpia el token actual para forzar renovación"""
        self.access_token = None
        self.token_expiry = None

    def get_auth_headers(self) -> dict:
        """Obtiene headers con token de autenticación"""
        token = self.get_valid_token()
        if token:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        return {"Content-Type": "application/json"}


# Instancia global del manejador de autenticación
backend_auth = BackendAuthManager()