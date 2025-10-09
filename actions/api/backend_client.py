"""
Cliente para el backend del sistema de ciudadanos
"""
import requests
import logging
from typing import Optional, Dict, Any, Tuple
from .backend_config import BackendConfig

logger = logging.getLogger(__name__)

"""
Cliente para el backend del sistema de ciudadanos con autenticación JWT
"""
import requests
import logging
from typing import Optional, Dict, Any, Tuple
from .backend_config import BackendConfig
from .backend_auth import backend_auth

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Cliente para APIs del backend del sistema con autenticación"""

    def __init__(self):
        self.base_url = BackendConfig.BASE_URL
        self.timeout = 30

    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers con token de autenticación"""
        return backend_auth.get_auth_headers()

    def _make_authenticated_request(
            self,
            method: str,
            url: str,
            **kwargs
    ) -> Optional[requests.Response]:
        """
        Realiza petición HTTP autenticada con manejo de token expirado

        Args:
            method: HTTP (GET, POST, PUT, etc.)
            url: URL completa del endpoint
            **kwargs: Argumentos adicionales para requests

        Returns:
            Response object o None si hay error
        """
        headers = self._get_headers()

        try:
            logger.info(f"{method} {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )

            # Si el token expiró (401), renovar e intentar de nuevo
            if response.status_code == 401:
                logger.warning("Token expirado, renovando...")
                backend_auth.clear_token()

                # Reintentar con nuevo token
                headers = self._get_headers()
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )

                if response.status_code == 401:
                    logger.error("Fallo en reintento después de renovar token")
                    return None
                else:
                    logger.info("Reintento exitoso con nuevo token")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"Timeout en petición: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión: {url}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en petición {url}: {e}")
            return None

    def get_citizen_data(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos básicos de un ciudadano por número de teléfono

        Args:
            phone_number: Número de teléfono del ciudadano

        Returns:
            Dict con datos del ciudadano o None si hay error/no existe
        """
        endpoint = BackendConfig.CITIZEN_GET_INFO.format(phone=phone_number)
        url = f"{self.base_url}{endpoint}"

        response = self._make_authenticated_request("GET", url)

        if response is None:
            return None

        if response.status_code == 200:
            logger.info(f"Datos del ciudadano obtenidos: {phone_number}")
            return response.json()
        elif response.status_code == 404:
            logger.info(f"Ciudadano no encontrado: {phone_number}")
            return None
        else:
            logger.error(f"Error obteniendo ciudadano {phone_number}: {response.status_code} - {response.text}")
            return None

    def close_assistance(self, phone_number: str) -> Tuple[bool, str]:
        """
        Cierra la asistencia activa para un ciudadano

        Args:
            phone_number: Número de teléfono del ciudadano

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        url = f"{self.base_url}{BackendConfig.ASSISTANCE_CLOSE}"

        payload = {
            "phoneNumber": phone_number
        }

        response = self._make_authenticated_request(
            "PUT",
            url,
            json=payload
        )

        if response is None:
            return False, "Error de conexión"

        if response.status_code in [200, 201]:
            data = response.json()
            success = data.get('success', False)
            message = data.get('message', 'Asistencia cerrada')

            if success:
                logger.info(f"Asistencia cerrada: {phone_number}")
                return True, message
            else:
                logger.warning(f"Backend reportó fallo: {phone_number}")
                return False, message
        else:
            logger.error(f"Error cerrando asistencia {phone_number}: {response.status_code}")
            return False, f"Error del servidor: {response.status_code}"

    def request_advisor(self, phone_number: str) -> Tuple[bool, str]:
        """
        Solicita un asesor humano para el ciudadano

        Args:
            phone_number: Número de teléfono del ciudadano

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        endpoint = BackendConfig.CITIZEN_REQUEST_ADVISOR.format(phone=phone_number)
        url = f"{self.base_url}{endpoint}"

        response = self._make_authenticated_request("POST", url)

        if response is None:
            return False, "Error de conexión con el servidor"

        if response.status_code in [200, 201]:
            data = response.json()
            message = data.get('message', 'Asesor solicitado exitosamente')
            logger.info(f"Asesor solicitado: {phone_number}")
            return True, message
        elif response.status_code == 404:
            logger.warning(f"Chat no encontrado: {phone_number}")
            return False, "No se encontró una conversación activa"
        else:
            logger.error(f"Error solicitando asesor {phone_number}: {response.status_code}")
            return False, f"Error del servidor: {response.status_code}"


# Instancia global del cliente backend
backend_client = BackendAPIClient()