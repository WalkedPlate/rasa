"""
Cliente para el backend del sistema de ciudadanos
"""
import requests
import logging
from typing import Optional, Dict, Any
from .backend_config import BackendConfig

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Cliente para APIs del backend del sistema"""

    def __init__(self):
        self.base_url = BackendConfig.BASE_URL
        self.timeout = 30
        self.default_headers = {
            "Content-Type": "application/json"
        }

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

        try:
            logger.info(f"Obteniendo datos del ciudadano: {phone_number}")

            response = requests.get(
                url=url,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                logger.info(f"Datos del ciudadano obtenidos exitosamente: {phone_number}")
                return response.json()

            elif response.status_code == 404:
                logger.info(f"Ciudadano no encontrado: {phone_number}")
                return None

            else:
                logger.error(f"Error obteniendo ciudadano {phone_number}: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Timeout obteniendo datos del ciudadano: {phone_number}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión obteniendo datos del ciudadano: {phone_number}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado obteniendo datos del ciudadano {phone_number}: {e}")
            return None

    def update_citizen_data(self, citizen_data: Dict[str, str]) -> bool:
        """
        Actualiza datos básicos de un ciudadano

        Args:
            citizen_data: Dict con los datos a actualizar
            Formato esperado:
            {
                "phoneNumber": "51962617808",
                "fullName": "Edward Josue Mamani Mamani",
                "documentType": "DNI",
                "documentNumber": "76577686"
            }

        Returns:
            bool: True si actualización exitosa, False si hay error
        """
        url = f"{self.base_url}{BackendConfig.CITIZEN_UPDATE}"

        try:
            logger.info(f"Actualizando datos del ciudadano: {citizen_data.get('phoneNumber')}")

            response = requests.put(
                url=url,
                json=citizen_data,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f"Datos actualizados exitosamente: {citizen_data.get('phoneNumber')}")
                return True
            else:
                logger.error(f"Error actualizando ciudadano: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"Timeout actualizando datos del ciudadano: {citizen_data.get('phoneNumber')}")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión actualizando datos del ciudadano: {citizen_data.get('phoneNumber')}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado actualizando datos del ciudadano: {e}")
            return False


# Instancia global del cliente backend
backend_client = BackendAPIClient()