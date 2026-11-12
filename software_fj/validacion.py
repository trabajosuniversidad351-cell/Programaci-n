"""Funciones de validación y conversión de entradas."""
from decimal import Decimal, InvalidOperation
import re
from .errores import DatosInvalidosError


def texto_obligatorio(valor: object, campo: str, longitud_minima: int = 1) -> str:
    if not isinstance(valor, str) or len(valor.strip()) < longitud_minima:
        raise DatosInvalidosError(f"{campo}: debe contener al menos {longitud_minima} caracteres.")
    return valor.strip()


def entero_positivo(valor: object, campo: str) -> int:
    if isinstance(valor, bool):
        raise DatosInvalidosError(f"{campo}: debe ser un entero positivo.")
    try:
        numero = int(valor)
    except (ValueError, TypeError, OverflowError) as exc:
        raise DatosInvalidosError(f"{campo}: debe ser un entero positivo.") from exc
    if str(valor).strip() != str(numero) and not isinstance(valor, int):
        raise DatosInvalidosError(f"{campo}: no se aceptan decimales.")
    if numero <= 0:
        raise DatosInvalidosError(f"{campo}: debe ser mayor que cero.")
    return numero


def decimal_no_negativo(valor: object, campo: str) -> Decimal:
    if isinstance(valor, bool):
        raise DatosInvalidosError(f"{campo}: debe ser un número válido.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise DatosInvalidosError(f"{campo}: debe ser un número válido.") from exc
    if not numero.is_finite() or numero < 0:
        raise DatosInvalidosError(f"{campo}: debe ser un número finito no negativo.")
    return numero


def decimal_positivo(valor: object, campo: str) -> Decimal:
    numero = decimal_no_negativo(valor, campo)
    if numero <= 0:
        raise DatosInvalidosError(f"{campo}: debe ser mayor que cero.")
    return numero


def porcentaje(valor: object, campo: str) -> Decimal:
    numero = decimal_no_negativo(valor, campo)
    if numero > 100:
        raise DatosInvalidosError(f"{campo}: no puede superar 100 %.")
    return numero


def validar_email(valor: object) -> str:
    correo = texto_obligatorio(valor, "Correo electrónico")
    if not re.fullmatch(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", correo, re.UNICODE):
        raise DatosInvalidosError("Correo electrónico: formato inválido.")
    return correo.lower()


def validar_telefono(valor: object) -> str:
    telefono = texto_obligatorio(valor, "Teléfono")
    if not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
        raise DatosInvalidosError("Teléfono: use entre 7 y 15 dígitos, opcionalmente +.")
    return telefono
