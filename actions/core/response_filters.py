"""
Filtros para separar respuestas de APIs del SAT por contexto
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ResponseFilter:
    """Filtros para separar papeletas e impuestos de las respuestas de API"""

    @staticmethod
    def filter_papeletas(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra solo papeletas/multas de tránsito de la respuesta de API

        Args:
            data_list: Lista de datos de la API del SAT

        Returns:
            List: Solo elementos que corresponden a papeletas
        """
        if not data_list or not isinstance(data_list, list):
            return []

        papeletas = []

        for item in data_list:
            # Criterios para identificar papeletas:
            # 1. Concepto explícito de "Papeletas"
            # 2. Tiene código de falta (campo 'falta' no vacío)
            # 3. Tiene fecha de infracción
            # 4. idconcepto específico de papeletas (587)

            concepto = item.get('concepto', '').strip()
            falta = item.get('falta', '').strip()
            fecha_infraccion = item.get('fechainfraccion', '').strip()
            id_concepto = item.get('idconcepto')

            es_papeleta = (
                    concepto == 'Papeletas' or
                    (falta and fecha_infraccion) or
                    id_concepto == 587 or
                    'Multa' in concepto or
                    'Infraccion' in concepto
            )

            if es_papeleta:
                papeletas.append(item)

        logger.debug(f"Filtrados {len(papeletas)} papeletas de {len(data_list)} elementos totales")
        return papeletas

    @staticmethod
    def filter_impuestos(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra solo impuestos y arbitrios de la respuesta de API

        Args:
            data_list: Lista de datos de la API del SAT

        Returns:
            List: Solo elementos que corresponden a impuestos
        """
        if not data_list or not isinstance(data_list, list):
            return []

        impuestos = []

        # Conceptos que identifican impuestos
        impuesto_conceptos = [
            'Imp. Predial',
            'Impuesto Predial',
            'Arbitrios',
            'Arbitrio',
            'Imp. Vehicular',
            'Impuesto Vehicular',
            'Alcabala',
            'Liquidacion Alcabala'
        ]

        # IDs de concepto específicos para impuestos
        impuesto_ids = [145, 200]  # 145: Predial, 200: Arbitrios

        for item in data_list:
            concepto = item.get('concepto', '').strip()
            id_concepto = item.get('idconcepto')
            falta = item.get('falta', '').strip()
            fecha_infraccion = item.get('fechainfraccion', '').strip()

            # Criterios para identificar impuestos:
            # 1. Concepto contiene palabras clave de impuestos
            # 2. ID de concepto específico de impuestos
            # 3. NO tiene código de falta (diferencia principal con papeletas)
            # 4. NO tiene fecha de infracción

            es_impuesto = (
                                  any(concepto_imp in concepto for concepto_imp in impuesto_conceptos) or
                                  id_concepto in impuesto_ids
                          ) and not (falta and fecha_infraccion)  # Excluir papeletas

            if es_impuesto:
                impuestos.append(item)

        logger.debug(f"Filtrados {len(impuestos)} impuestos de {len(data_list)} elementos totales")
        return impuestos

    @staticmethod
    def has_papeletas(data_list: List[Dict[str, Any]]) -> bool:
        """
        Verifica si la respuesta contiene papeletas

        Args:
            data_list: Lista de datos de la API

        Returns:
            bool: True si contiene papeletas
        """
        papeletas = ResponseFilter.filter_papeletas(data_list)
        return len(papeletas) > 0

    @staticmethod
    def has_impuestos(data_list: List[Dict[str, Any]]) -> bool:
        """
        Verifica si la respuesta contiene impuestos

        Args:
            data_list: Lista de datos de la API

        Returns:
            bool: True si contiene impuestos
        """
        impuestos = ResponseFilter.filter_impuestos(data_list)
        return len(impuestos) > 0

    @staticmethod
    def get_summary(data_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Obtiene resumen de tipos de datos en la respuesta

        Args:
            data_list: Lista de datos de la API

        Returns:
            Dict: Resumen con conteos por tipo
        """
        if not data_list:
            return {'papeletas': 0, 'impuestos': 0, 'otros': 0}

        papeletas = ResponseFilter.filter_papeletas(data_list)
        impuestos = ResponseFilter.filter_impuestos(data_list)
        otros = len(data_list) - len(papeletas) - len(impuestos)

        return {
            'papeletas': len(papeletas),
            'impuestos': len(impuestos),
            'otros': max(0, otros)
        }


# Instancia global del filtro
response_filter = ResponseFilter()