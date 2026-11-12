"""Gestor en memoria para clientes, servicios y reservas."""
import logging
from pathlib import Path
from typing import Callable, TypeVar
from .entidades import Cliente
from .errores import (DatosInvalidosError, ErrorSistema,
                      RecursoNoEncontradoError, RegistroDuplicadoError)
from .reservas import Reserva
from .servicios import Servicio
from .validacion import texto_obligatorio

T = TypeVar("T")


def preparar_logger(carpeta: Path | None = None) -> logging.Logger:
    """Crea un archivo persistente para eventos y errores, sin guardar datos."""
    carpeta = carpeta or (Path(__file__).resolve().parent.parent / "logs")
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = (carpeta / "eventos.log").resolve()
    logger = logging.getLogger("software_fj")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for manejador in logger.handlers:
        if isinstance(manejador, logging.FileHandler) and Path(manejador.baseFilename) == ruta:
            return logger
    manejador = logging.FileHandler(ruta, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(manejador)
    return logger


class GestorReservas:
    """Mantiene los datos de negocio únicamente en diccionarios en memoria."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: dict[str, Reserva] = {}
        self.logger = logger or preparar_logger()

    def registrar_cliente(self, identificador: str, nombre: str, correo: str, telefono: str) -> Cliente:
        """Ejemplo de try/except/else y de recuperación de errores."""
        try:
            cliente = Cliente(identificador, nombre, correo, telefono)
            if cliente.identificador in self._clientes:
                raise RegistroDuplicadoError(f"Cliente duplicado: {cliente.identificador}.")
        except ErrorSistema as exc:
            self.logger.error("Registro de cliente rechazado: %s", exc)
            raise
        else:
            self._clientes[cliente.identificador] = cliente
            self.logger.info("Cliente registrado: %s", cliente.identificador)
            return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto proporcionado no es un servicio válido.")
        if servicio.identificador in self._servicios:
            raise RegistroDuplicadoError(f"Servicio duplicado: {servicio.identificador}.")
        self._servicios[servicio.identificador] = servicio
        self.logger.info("Servicio registrado: %s (%s)", servicio.identificador, type(servicio).__name__)
        return servicio

    @staticmethod
    def _obtener(coleccion: dict[str, T], identificador: str, nombre: str) -> T:
        clave = texto_obligatorio(identificador, f"Identificador de {nombre}")
        try:
            return coleccion[clave]
        except KeyError as exc:
            raise RecursoNoEncontradoError(f"{nombre.capitalize()} no encontrado: {clave}.") from exc

    def obtener_cliente(self, identificador: str) -> Cliente:
        return self._obtener(self._clientes, identificador, "cliente")

    def obtener_servicio(self, identificador: str) -> Servicio:
        return self._obtener(self._servicios, identificador, "servicio")

    def obtener_reserva(self, identificador: str) -> Reserva:
        return self._obtener(self._reservas, identificador, "reserva")

    def crear_reserva(self, identificador: str, cliente_id: str, servicio_id: str,
                      duracion: int, impuesto: object = 0, descuento: object = 0) -> Reserva:
        """Evita cambios parciales si falla la construcción de una reserva."""
        clave = texto_obligatorio(identificador, "Identificador de reserva")
        if clave in self._reservas:
            raise RegistroDuplicadoError(f"Reserva duplicada: {clave}.")
        cliente = self.obtener_cliente(cliente_id)
        servicio = self.obtener_servicio(servicio_id)
        reserva = Reserva(clave, cliente, servicio, duracion, impuesto, descuento)
        self._reservas[clave] = reserva
        self.logger.info("Reserva creada: %s", clave)
        return reserva

    def confirmar_reserva(self, reserva_id: str) -> Reserva:
        reserva = self.obtener_reserva(reserva_id)
        reserva.confirmar()
        self.logger.info("Reserva confirmada: %s", reserva_id)
        return reserva

    def procesar_reserva(self, reserva_id: str) -> Reserva:
        """Ejemplo de try/except/finally para registrar la terminación."""
        try:
            reserva = self.obtener_reserva(reserva_id)
            reserva.procesar()
        except ErrorSistema as exc:
            self.logger.error("No se pudo procesar la reserva %s: %s", reserva_id, exc)
            raise
        else:
            self.logger.info("Reserva procesada: %s", reserva_id)
            return reserva
        finally:
            self.logger.info("Finalizó intento de procesamiento: %s", reserva_id)

    def cancelar_reserva(self, reserva_id: str) -> Reserva:
        reserva = self.obtener_reserva(reserva_id)
        reserva.cancelar()
        self.logger.info("Reserva cancelada: %s", reserva_id)
        return reserva

    @property
    def clientes(self) -> list[Cliente]:
        return list(self._clientes.values())

    @property
    def servicios(self) -> list[Servicio]:
        return list(self._servicios.values())

    @property
    def reservas(self) -> list[Reserva]:
        return list(self._reservas.values())
