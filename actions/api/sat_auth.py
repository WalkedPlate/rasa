"""
Manejo de autenticación automática con la API del SAT
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class SATAuthManager:
    """Maneja la autenticación automática con la API del SAT"""

    def __init__(self):
        self.token = None
        self.token_expiry = None
        self.auth_url = "https://ws.sat.gob.pe/auth/login"
        self.credentials = {
            "client_id": "ChatBootSat",
            "client_secret": "4qp3hETQRbdyt20o6762a33dMEpr3Bqx",
            "usuario": "usrchatbootsat",
            "clave": "PQb%qd72E@%4cCnmkyT*"
        }

    def get_valid_token(self) -> Optional[str]:
        """Obtiene un token válido, renovándolo si es necesario"""
        if self.token is None or self.is_token_expired():
            self.refresh_token()
        return self.token

    def is_token_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        if self.token_expiry is None:
            return True
        return datetime.now() >= (self.token_expiry - timedelta(minutes=1))

    def refresh_token(self) -> bool:
        """Obtiene un nuevo token de la API"""
        try:
            logger.info(" Renovando token de autenticación SAT...")

            response = requests.post(
                self.auth_url,
                json=self.credentials,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                expires_in = data.get("expires_in", 900)  # Default 15 min
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

                logger.info(f" Token renovado exitosamente, expira en {expires_in} segundos")
                return True
            else:
                logger.error(f" Error obteniendo token: {response.status_code} - {response.text}")
                self.token = None
                return False

        except Exception as e:
            logger.error(f" Error en autenticación: {e}")
            self.token = None
            return False

    def clear_token(self):
        """Limpia el token actual para forzar renovación"""
        self.token = None
        self.token_expiry = None


# Instancia global del manejador de autenticación
auth_manager = SATAuthManager()