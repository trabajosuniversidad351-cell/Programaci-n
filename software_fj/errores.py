"""Excepciones del sistema de reservas."""


class ErrorSistema(Exception):
    """Excepción base para errores controlados de la aplicación."""


class DatosInvalidosError(ErrorSistema):
    """Se recibió información que no cumple las validaciones."""


class RecursoNoEncontradoError(ErrorSistema):
    """Un cliente, servicio o reserva solicitado no existe."""


class RegistroDuplicadoError(ErrorSistema):
    """Se intentó registrar una entidad con identificador repetido."""


class ServicioNoDisponibleError(ErrorSistema):
    """No hay disponibilidad para el servicio solicitado."""


class OperacionNoPermitidaError(ErrorSistema):
    """El estado actual impide realizar una operación."""
