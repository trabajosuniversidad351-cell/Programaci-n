"""Servicios abstractos y especializados con polimorfismo."""
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import overload
from .entidades import Entidad
from .errores import ServicioNoDisponibleError
from .validacion import decimal_positivo, entero_positivo, porcentaje, texto_obligatorio


class Servicio(Entidad, ABC):
    """Contrato común a los servicios de la empresa."""

    def __init__(self, identificador: str, nombre: str, cupos: int) -> None:
        super().__init__(identificador)
        self._nombre = texto_obligatorio(nombre, "Nombre de servicio")
        self._cupos = entero_positivo(cupos, "Cupos")
        self._ocupados = 0

    @property
    def cupos_disponibles(self) -> int:
        return self._cupos - self._ocupados

    @property
    def nombre(self) -> str:
        return self._nombre

    def validar_parametros(self, duracion: object) -> int:
        """Valida el tiempo solicitado; las subclases pueden restringirlo."""
        return entero_positivo(duracion, "Duración")

    @abstractmethod
    def _costo_base(self, duracion: int) -> Decimal:
        """Se redefine para cada tipo de servicio."""

    @overload
    def calcular_costo(self, duracion: int) -> Decimal: ...

    @overload
    def calcular_costo(self, duracion: int, impuesto: object) -> Decimal: ...

    @overload
    def calcular_costo(self, duracion: int, impuesto: object, descuento: object) -> Decimal: ...

    def calcular_costo(self, duracion: int, impuesto: object = 0, descuento: object = 0) -> Decimal:
        """Admite variantes: precio base, con impuesto y con descuento.

        Python no despacha sobrecargas por cantidad de parámetros; estas
        variantes se expresan con @overload y una implementación común.
        """
        tiempo = self.validar_parametros(duracion)
        tasa = porcentaje(impuesto, "Impuesto")
        rebaja = porcentaje(descuento, "Descuento")
        subtotal = self._costo_base(tiempo)
        total = subtotal * (Decimal(1) - rebaja / 100) * (Decimal(1) + tasa / 100)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def ocupar_cupo(self) -> None:
        if self.cupos_disponibles <= 0:
            raise ServicioNoDisponibleError(f"No hay cupos para {self.nombre}.")
        self._ocupados += 1

    def liberar_cupo(self) -> None:
        if self._ocupados > 0:
            self._ocupados -= 1


class ReservaSala(Servicio):
    """Servicio de reserva de salas, cobrado por hora."""

    def __init__(self, identificador: str, nombre: str, tarifa_hora: object, capacidad: int, cupos: int = 1) -> None:
        super().__init__(identificador, nombre, cupos)
        self._tarifa = decimal_positivo(tarifa_hora, "Tarifa por hora")
        self._capacidad = entero_positivo(capacidad, "Capacidad de personas")

    def validar_parametros(self, duracion: object) -> int:
        horas = super().validar_parametros(duracion)
        if horas > 12:
            from .errores import DatosInvalidosError
            raise DatosInvalidosError("Reserva de sala: máximo 12 horas por solicitud.")
        return horas

    def _costo_base(self, duracion: int) -> Decimal:
        return self._tarifa * duracion

    def describir(self) -> str:
        return f"Sala {self.nombre} ({self._capacidad} personas), ${self._tarifa}/hora; cupos: {self.cupos_disponibles}."


class AlquilerEquipo(Servicio):
    """Servicio de equipos, cobrado por día."""

    def __init__(self, identificador: str, nombre: str, tarifa_dia: object, cupos: int) -> None:
        super().__init__(identificador, nombre, cupos)
        self._tarifa = decimal_positivo(tarifa_dia, "Tarifa por día")

    def validar_parametros(self, duracion: object) -> int:
        dias = super().validar_parametros(duracion)
        if dias > 30:
            from .errores import DatosInvalidosError
            raise DatosInvalidosError("Alquiler de equipo: máximo 30 días.")
        return dias

    def _costo_base(self, duracion: int) -> Decimal:
        return self._tarifa * duracion

    def describir(self) -> str:
        return f"Equipo {self.nombre}, ${self._tarifa}/día; unidades disponibles: {self.cupos_disponibles}."


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría, cobrado por hora."""

    def __init__(self, identificador: str, nombre: str, especialidad: str, tarifa_hora: object, cupos: int = 1) -> None:
        super().__init__(identificador, nombre, cupos)
        self._especialidad = texto_obligatorio(especialidad, "Especialidad", 3)
        self._tarifa = decimal_positivo(tarifa_hora, "Tarifa por hora")

    def validar_parametros(self, duracion: object) -> int:
        horas = super().validar_parametros(duracion)
        if horas > 8:
            from .errores import DatosInvalidosError
            raise DatosInvalidosError("Asesoría: máximo 8 horas.")
        return horas

    def _costo_base(self, duracion: int) -> Decimal:
        return self._tarifa * duracion

    def describir(self) -> str:
        return f"Asesoría {self.nombre}, área {self._especialidad}, ${self._tarifa}/hora; cupos: {self.cupos_disponibles}."
