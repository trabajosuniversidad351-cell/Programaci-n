"""Entidades y clientes con abstracción y encapsulación."""
from abc import ABC, abstractmethod
from .validacion import texto_obligatorio, validar_email, validar_telefono


class Entidad(ABC):
    """Clase abstracta para objetos identificables."""

    def __init__(self, identificador: str) -> None:
        self._identificador = texto_obligatorio(identificador, "Identificador")

    @property
    def identificador(self) -> str:
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción de la entidad."""


class Cliente(Entidad):
    """Cliente cuyos datos se almacenan en atributos encapsulados."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(identificador)
        self.__nombre = texto_obligatorio(nombre, "Nombre", 3)
        self.__correo = validar_email(correo)
        self.__telefono = validar_telefono(telefono)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def cambiar_correo(self, correo: str) -> None:
        self.__correo = validar_email(correo)

    def describir(self) -> str:
        return f"Cliente {self.identificador}: {self.nombre} ({self.correo})"
