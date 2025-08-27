"""
Validadores para datos de entrada (DNI, placa, RUC, códigos, trámites)
"""
import re
from typing import Tuple, Optional


class DataValidator:
    """Clase para validar formatos de datos peruanos"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Limpia texto removiendo espacios y caracteres especiales"""
        if not text:
            return ""
        return text.strip().upper()

    @staticmethod
    def validate_placa(placa: str) -> Tuple[bool, str]:
        """
        Valida formato de placa vehicular peruana

        Args:
            placa: Número de placa a validar

        Returns:
            Tuple[bool, str]: (es_válida, placa_limpia)
        """
        if not placa:
            return False, ""

        # Limpiar placa
        placa_limpia = re.sub(r'[^A-Z0-9]', '', placa.strip().upper())

        # Patrones de placas peruanas
        patrones_validos = [
            r'^[A-Z]{3}[0-9]{3}$',  # ABC123 (clásico)
            r'^[A-Z]{2}[0-9]{4}$',  # AB1234 (clásico)
            r'^[A-Z][0-9][A-Z][0-9]{3}$',  # A1B234 (nuevo formato)
            r'^[A-Z]{2}[0-9][A-Z][0-9]{2}$',  # AB1C23 (variante)
            r'^[A-Z0-9]{6}$' # GENERAL
        ]

        es_valida = any(re.match(patron, placa_limpia) for patron in patrones_validos)
        return es_valida, placa_limpia

    @staticmethod
    def validate_dni(dni: str) -> Tuple[bool, str]:
        """
        Valida formato de DNI peruano

        Args:
            dni: Número de DNI a validar

        Returns:
            Tuple[bool, str]: (es_válido, dni_limpio)
        """
        if not dni:
            return False, ""

        # Limpiar DNI (solo números)
        dni_limpio = re.sub(r'[^0-9]', '', dni.strip())

        # DNI debe tener exactamente 8 dígitos
        es_valido = len(dni_limpio) == 8 and dni_limpio.isdigit()

        return es_valido, dni_limpio

    @staticmethod
    def validate_ruc(ruc: str) -> Tuple[bool, str]:
        """
        Valida formato de RUC peruano

        Args:
            ruc: Número de RUC a validar

        Returns:
            Tuple[bool, str]: (es_válido, ruc_limpio)
        """
        if not ruc:
            return False, ""

        # Limpiar RUC (solo números)
        ruc_limpio = re.sub(r'[^0-9]', '', ruc.strip())

        # RUC debe tener exactamente 11 dígitos
        if len(ruc_limpio) != 11 or not ruc_limpio.isdigit():
            return False, ruc_limpio

        # Validar primer dígito (tipo de contribuyente)
        primer_digito = ruc_limpio[0]
        if primer_digito not in ['1', '2']:
            return False, ruc_limpio

        return True, ruc_limpio

    @staticmethod
    def validate_codigo_falta(codigo: str) -> Tuple[bool, str]:
        """
        Valida formato de código de falta

        Args:
            codigo: Código de falta a validar

        Returns:
            Tuple[bool, str]: (es_válido, codigo_limpio)
        """
        if not codigo:
            return False, ""

        # Limpiar código
        codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo.strip().upper())

        # Patrones válidos para códigos de falta
        patrones_validos = [
            r'^[A-Z][0-9]{2}$',  # A05, C15, M08
            r'^[A-Z][0-9]{1}$',  # A5, C1, M8
            r'^[0-9]{3}$',  # 001, 125
        ]

        es_valido = any(re.match(patron, codigo_limpio) for patron in patrones_validos)
        return es_valido, codigo_limpio

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
    def detect_data_type(text: str) -> Optional[str]:
        """
        Detecta automáticamente el tipo de dato basado en el formato

        Args:
            text: Texto a analizar

        Returns:
            str: 'placa', 'dni', 'ruc', 'codigo_falta' o None
        """
        if not text:
            return None

        text_limpio = text.strip().upper()

        # Verificar cada tipo
        es_placa, _ = DataValidator.validate_placa(text_limpio)
        if es_placa:
            return 'placa'

        es_dni, _ = DataValidator.validate_dni(text_limpio)
        if es_dni:
            return 'dni'

        es_ruc, _ = DataValidator.validate_ruc(text_limpio)
        if es_ruc:
            return 'ruc'

        es_codigo, _ = DataValidator.validate_codigo_falta(text_limpio)
        if es_codigo:
            return 'codigo_falta'

        return None

    @staticmethod
    def get_validation_message(data_type: str, is_valid: bool, value: str) -> str:
        """
        Genera mensaje de validación específico para cada tipo de dato

        Args:
            data_type: Tipo de dato ('placa', 'dni', etc.)
            is_valid: Si el dato es válido
            value: Valor proporcionado

        Returns:
            str: Mensaje de validación
        """
        if is_valid:
            return f"✅ {data_type.upper()} válido: {value}"

        error_messages = {
            'placa': f" La placa '{value}' no tiene un formato válido.\n\n **Formatos correctos:**\n• ABC123 (clásico)\n• AB1234 (clásico)\n• U1A710 (nuevo formato)\n• A1B234 (nuevo formato)",
            'dni': f" El DNI '{value}' no es válido. Debe tener exactamente 8 dígitos.",
            'ruc': f" El RUC '{value}' no es válido. Debe tener 11 dígitos y empezar con 1 o 2.",
            'codigo_falta': f" El código '{value}' no es válido. Formato esperado: C15, M08, A05, etc."
        }

        return error_messages.get(data_type, f" Dato '{value}' no es válido.")

    @staticmethod
    def validate_codigo_contribuyente(codigo: str) -> Tuple[bool, str]:
        """
        Valida formato de código de contribuyente

        Args:
            codigo: Código de contribuyente a validar

        Returns:
            Tuple[bool, str]: (es_válido, codigo_limpio)
        """
        if not codigo:
            return False, ""

        # Limpiar código (solo números)
        codigo_limpio = re.sub(r'[^0-9]', '', codigo.strip())

        # Código de contribuyente debe ser numérico y tener entre 1 y 10 dígitos
        if not codigo_limpio.isdigit():
            return False, codigo_limpio

        # Validar longitud (típicamente entre 1 y 10 dígitos)
        if len(codigo_limpio) < 1 or len(codigo_limpio) > 10:
            return False, codigo_limpio

        return True, codigo_limpio

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Valida formato de número de teléfono

        Args:
            phone: Número de teléfono a validar

        Returns:
            Tuple[bool, str]: (es_válido, phone_limpio)
        """
        if not phone:
            return False, ""

        # Limpiar teléfono (solo números)
        phone_limpio = re.sub(r'[^0-9]', '', phone.strip())

        if not phone_limpio.isdigit():
            return False, phone_limpio

        return True, phone_limpio

    @staticmethod
    def detect_data_type(text: str) -> Optional[str]:
        """
        Detecta automáticamente el tipo de dato basado en el formato

        Args:
            text: Texto a analizar

        Returns:
            str: 'placa', 'dni', 'ruc', 'codigo_falta', 'codigo_contribuyente' o None
        """
        if not text:
            return None

        text_limpio = text.strip().upper()

        # Verificar cada tipo en orden de especificidad
        es_placa, _ = DataValidator.validate_placa(text_limpio)
        if es_placa:
            return 'placa'

        es_dni, _ = DataValidator.validate_dni(text_limpio)
        if es_dni:
            return 'dni'

        es_ruc, _ = DataValidator.validate_ruc(text_limpio)
        if es_ruc:
            return 'ruc'

        es_codigo_falta, _ = DataValidator.validate_codigo_falta(text_limpio)
        if es_codigo_falta:
            return 'codigo_falta'

        es_codigo_contribuyente, _ = DataValidator.validate_codigo_contribuyente(text_limpio)
        if es_codigo_contribuyente:
            return 'codigo_contribuyente'

        return None

    @staticmethod
    def get_validation_message(data_type: str, is_valid: bool, value: str) -> str:
        """
        Genera mensaje de validación específico para cada tipo de dato

        Args:
            data_type: Tipo de dato ('placa', 'dni', etc.)
            is_valid: Si el dato es válido
            value: Valor proporcionado

        Returns:
            str: Mensaje de validación
        """
        if is_valid:
            return f"Dato {data_type.upper().replace('_', ' ')} válido: {value}"

        error_messages = {
            'placa': f"La placa '{value}' no tiene un formato válido.\n\n**Formatos correctos:**\n• ABC123 (clásico)\n• AB1234 (clásico)\n• U1A710 (nuevo formato)\n• A1B234 (nuevo formato)",
            'dni': f"El DNI '{value}' no es válido. Debe tener exactamente 8 dígitos.",
            'ruc': f"El RUC '{value}' no es válido. Debe tener 11 dígitos y empezar con 1 o 2.",
            'codigo_falta': f"El código '{value}' no es válido. Formato esperado: C15, M08, A05, etc.",
            'codigo_contribuyente': f"El código de contribuyente '{value}' no es válido. Debe ser numérico de 1 a 10 dígitos.",
            'phone_number': f"El número de teléfono '{value}' no es válido. Debe tener solo dígitos."
        }

        return error_messages.get(data_type, f"Dato '{value}' no es válido.")

# Instancia global del validador
validator = DataValidator()