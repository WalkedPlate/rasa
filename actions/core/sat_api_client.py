"""
Cliente base para APIs del SAT con manejo automático de autenticación
"""
import requests
import logging
from typing import Optional, Dict, Any, Tuple
from .auth_manager import auth_manager

logger = logging.getLogger(__name__)

class SATAPIClient:
    """Cliente base para todas las APIs del SAT"""

    def __init__(self):
        self.base_url = "https://ws.sat.gob.pe"
        self.timeout = 30
        self.default_headers = {
            "Content-Type": "application/json",
            "IP": "172.168.1.1"
        }

    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers con token de autenticación"""
        headers = self.default_headers.copy()

        token = auth_manager.get_valid_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Realiza una petición HTTP con manejo de errores y reintentosrequests

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            **kwargs: Argumentos adicionales para requests

        Returns:
            Dict con la respuesta o None si hay error
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            logger.info(f"🌐 {method} {endpoint}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
                **kwargs
            )

            if response.status_code == 200:
                logger.info(f"✅ Respuesta exitosa: {response.status_code}")
                return response.json()

            elif response.status_code == 401:
                # Token expirado, renovar y reintentar
                logger.warning("🔄 Token expirado, renovando...")
                auth_manager.clear_token()

                # Reintentar con nuevo token
                headers = self._get_headers()
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.timeout,
                    verify=False,
                    **kwargs
                )

                if response.status_code == 200:
                    logger.info("✅ Reintento exitoso después de renovar token")
                    return response.json()
                else:
                    logger.error(f"❌ Error en reintento: {response.status_code}")
                    return None

            else:
                logger.error(f"❌ Error API SAT: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout en petición a API SAT")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("🌐 Error de conexión con API SAT")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado en API SAT: {e}")
            return None

    def consultar_papeletas_por_ruc(self, ruc: str) -> Optional[Dict[str, Any]]:
        """
        Consulta papeletas por RUC

        Args:
            ruc: Número de RUC

        Returns:
            Dict con resultado de la consulta
        """
        endpoint = f"/saldomatico/saldomatico/chatboot/1/{ruc}/0/10/11"
        return self._make_request("GET", endpoint)

    def consultar_papeletas_por_dni(self, dni: str) -> Optional[Dict[str, Any]]:
        """
        Consulta papeletas por DNI

        Args:
            dni: Número de DNI

        Returns:
            Dict con resultado de la consulta
        """
        endpoint = f"/saldomatico/saldomatico/chatboot/2/{dni}/0/10/11"
        return self._make_request("GET", endpoint)

    def consultar_papeletas_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Consulta papeletas por placa

        Args:
            placa: Número de placa vehicular

        Returns:
            Dict con resultado de la consulta
        """
        endpoint = f"/saldomatico/saldomatico/chatboot/3/{placa}/0/10/11"
        return self._make_request("GET", endpoint)

    def consultar_codigo_falta(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Consulta información de código de falta

        Args:
            codigo: Código de falta (ej: C15, M08, G40)

        Returns:
            Dict con información del código
        """
        endpoint = f"/saldomatico/falta/{codigo}"
        return self._make_request("GET", endpoint)

    def consultar_por_codigo_contribuyente(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Consulta deuda por código de contribuyente

        Args:
            codigo: Código de contribuyente (ej: 94539)

        Returns:
            Dict con resultado de la consulta
        """
        endpoint = f"/saldomatico/saldomatico/chatboot/5/{codigo}/0/10/10"
        return self._make_request("GET", endpoint)

    def consultar_orden_captura_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Consulta órdenes de captura por placa vehicular

        Args:
            placa: Número de placa vehicular

        Returns:
            Dict con resultado de la consulta de órdenes de captura
        """
        endpoint = f"/saldomatico/papeleta/chatboot/{placa}"
        return self._make_request("GET", endpoint)

    @staticmethod
    def validate_numero_tramite(numero: str) -> Tuple[bool, str]:
        """
        Valida formato de número de trámite (14 dígitos)

        Args:
            numero: Número de trámite a validar

        Returns:
            Tuple[bool, str]: (es_válido, numero_limpio)
        """
        if not numero:
            return False, ""

        # Limpiar número (solo números)
        numero_limpio = re.sub(r'[^0-9]', '', numero.strip())

        # Número de trámite debe tener exactamente 14 dígitos
        es_valido = len(numero_limpio) == 14 and numero_limpio.isdigit()

        return es_valido, numero_limpio

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Formatea fecha al formato dd-MM-yyyy

        Args:
            date_str: Fecha en formato original

        Returns:
            str: Fecha formateada en dd-MM-yyyy o original si no se puede formatear
        """
        if not date_str or date_str.strip() == "":
            return "No disponible"

        try:
            # Intentar varios formatos de entrada comunes
            possible_formats = [
                "%Y-%m-%d",  # 2024-01-15
                "%Y-%m-%dT%H:%M:%S",  # 2024-01-15T10:30:00
                "%d/%m/%Y",  # 15/01/2024
                "%d-%m-%Y",  # 15-01-2024
            ]

            for fmt in possible_formats:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.strftime("%d-%m-%Y")
                except ValueError:
                    continue

            # Si no se puede parsear, devolver original
            return date_str.strip()

        except Exception:
            return date_str.strip() if date_str else "No disponible"

    def health_check(self) -> bool:
        """
        Verifica que la API esté disponible

        Returns:
            bool: True si la API responde correctamente
        """
        try:
            # Intentar renovar token como health check
            return auth_manager.refresh_token()
        except Exception:
            return False

# Instancia global del cliente API
sat_client = SATAPIClient()