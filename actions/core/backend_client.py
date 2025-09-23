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

    def close_assistance(self, phone_number: str) -> Tuple[bool, str]:
        """
        Cierra la asistencia activa para un ciudadano por número de teléfono

        Args:
            phone_number: Número de teléfono del ciudadano

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        url = f"{self.base_url}{BackendConfig.ASSISTANCE_CLOSE}"

        payload = {
            "phoneNumber": phone_number
        }

        try:
            logger.info(f"Cerrando asistencia para: {phone_number}")

            response = requests.put(
                url=url,
                json=payload,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', 'Asistencia cerrada')

                if success:
                    logger.info(f"Asistencia cerrada exitosamente: {phone_number}")
                    return True, message
                else:
                    logger.warning(f"Backend reportó fallo al cerrar asistencia: {phone_number}")
                    return False, message

            else:
                logger.error(f"Error cerrando asistencia {phone_number}: {response.status_code} - {response.text}")
                return False, f"Error del servidor: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error(f"Timeout cerrando asistencia: {phone_number}")
            return False, "Timeout en la conexión"
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión cerrando asistencia: {phone_number}")
            return False, "Error de conexión"
        except Exception as e:
            logger.error(f"Error inesperado cerrando asistencia {phone_number}: {e}")
            return False, f"Error inesperado: {str(e)}"

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

        try:
            logger.info(f"Solicitando asesor para: {phone_number}")

            response = requests.post(
                url=url,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                data = response.json()
                message = data.get('message', 'Asesor solicitado exitosamente')
                logger.info(f"Asesor solicitado exitosamente: {phone_number}")
                return True, message

            elif response.status_code == 404:
                logger.warning(f"Chat no encontrado para: {phone_number}")
                return False, "No se encontró una conversación activa"

            else:
                logger.error(f"Error solicitando asesor {phone_number}: {response.status_code} - {response.text}")
                return False, f"Error del servidor: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error(f"Timeout solicitando asesor: {phone_number}")
            return False, "Timeout en la conexión"
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión solicitando asesor: {phone_number}")
            return False, "Error de conexión con el servidor"
        except Exception as e:
            logger.error(f"Error inesperado solicitando asesor {phone_number}: {e}")
            return False, f"Error inesperado: {str(e)}"


# Instancia global del cliente backend
backend_client = BackendAPIClient()