"""Reserva, estados y transiciones controladas."""
from decimal import Decimal
from enum import Enum
from .entidades import Cliente, Entidad
from .errores import OperacionNoPermitidaError
from .servicios import Servicio


class EstadoReserva(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(Entidad):
    """Une cliente, servicio, duración, costo y estado de una solicitud."""

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio,
                 duracion: int, impuesto: object = 0, descuento: object = 0) -> None:
        super().__init__(identificador)
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = servicio.validar_parametros(duracion)
        self._total = servicio.calcular_costo(self._duracion, impuesto, descuento)
        self._estado = EstadoReserva.PENDIENTE

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def total(self) -> Decimal:
        return self._total

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    def confirmar(self) -> None:
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError("Solo se puede confirmar una reserva pendiente.")
        self._servicio.ocupar_cupo()
        self._estado = EstadoReserva.CONFIRMADA

    def procesar(self) -> None:
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError("Solo se puede procesar una reserva confirmada.")
        self._estado = EstadoReserva.PROCESADA

    def cancelar(self) -> None:
        if self._estado is EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya está cancelada.")
        if self._estado is EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError("No se puede cancelar una reserva procesada.")
        if self._estado is EstadoReserva.CONFIRMADA:
            self._servicio.liberar_cupo()
        self._estado = EstadoReserva.CANCELADA

    def describir(self) -> str:
        return (f"Reserva {self.identificador}: {self._cliente.nombre} | "
                f"{self._servicio.nombre} | duración {self._duracion} | "
                f"${self._total} | {self._estado.value}")
