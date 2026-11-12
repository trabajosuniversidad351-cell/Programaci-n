"""Pruebas unitarias de reglas de negocio y excepciones."""
import logging
import unittest
from decimal import Decimal
from software_fj import (AlquilerEquipo, AsesoriaEspecializada,
                         Cliente, EstadoReserva, GestorReservas, ReservaSala)
from software_fj.errores import (DatosInvalidosError, OperacionNoPermitidaError,
                                RecursoNoEncontradoError, RegistroDuplicadoError,
                                ServicioNoDisponibleError)


class PruebasSoftwareFJ(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("pruebas.software_fj")
        self.gestor = GestorReservas(logger=self.logger)
        self.gestor.registrar_cliente("C1", "Ana Pruebas", "ana@example.com", "3001112233")
        self.sala = ReservaSala("S1", "Sala", 50000, 10, 1)
        self.equipo = AlquilerEquipo("S2", "Portátil", 30000, 1)
        self.asesoria = AsesoriaEspecializada("S3", "Asesor", "Redes", 75000)
        for servicio in (self.sala, self.equipo, self.asesoria):
            self.gestor.registrar_servicio(servicio)

    def test_01_cliente_valido(self):
        self.assertEqual(self.gestor.obtener_cliente("C1").nombre, "Ana Pruebas")

    def test_02_cliente_correo_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Cliente("C2", "Prueba Correo", "incorrecto", "3001234567")

    def test_03_cliente_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.registrar_cliente("C1", "Otra Persona", "otra@example.com", "3001234567")

    def test_04_encapsulacion_cambio_correo(self):
        cliente = self.gestor.obtener_cliente("C1")
        cliente.cambiar_correo("NUEVO@EXAMPLE.COM")
        self.assertEqual(cliente.correo, "nuevo@example.com")

    def test_05_rechazo_tarifa_negativa(self):
        with self.assertRaises(DatosInvalidosError):
            ReservaSala("S4", "Incorrecta", -2, 5)

    def test_06_polimorfismo_tres_costos(self):
        self.assertEqual([s.calcular_costo(2) for s in (self.sala, self.equipo, self.asesoria)],
                         [Decimal("100000.00"), Decimal("60000.00"), Decimal("150000.00")])

    def test_07_calculo_con_impuesto_y_descuento(self):
        self.assertEqual(self.sala.calcular_costo(2, 19, 10), Decimal("107100.00"))

    def test_08_descuento_mayor_a_cien(self):
        with self.assertRaises(DatosInvalidosError):
            self.sala.calcular_costo(2, 19, 101)

    def test_09_duracion_invalida(self):
        with self.assertRaises(DatosInvalidosError):
            self.gestor.crear_reserva("R1", "C1", "S1", 0)

    def test_10_cliente_inexistente(self):
        with self.assertRaises(RecursoNoEncontradoError):
            self.gestor.crear_reserva("R1", "C99", "S1", 1)

    def test_11_cadena_excepciones(self):
        with self.assertRaises(RecursoNoEncontradoError) as contexto:
            self.gestor.obtener_cliente("C99")
        self.assertIsInstance(contexto.exception.__cause__, KeyError)

    def test_12_crear_reserva_pendiente(self):
        reserva = self.gestor.crear_reserva("R1", "C1", "S1", 2)
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)

    def test_13_confirmar_reserva(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 2)
        self.assertEqual(self.gestor.confirmar_reserva("R1").estado, EstadoReserva.CONFIRMADA)
        self.assertEqual(self.sala.cupos_disponibles, 0)

    def test_14_confirmacion_sin_cupo(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        self.gestor.crear_reserva("R2", "C1", "S1", 1)
        self.gestor.confirmar_reserva("R1")
        with self.assertRaises(ServicioNoDisponibleError):
            self.gestor.confirmar_reserva("R2")
        self.assertEqual(self.gestor.obtener_reserva("R2").estado, EstadoReserva.PENDIENTE)

    def test_15_cancelar_devuelve_cupo(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        self.gestor.confirmar_reserva("R1")
        self.gestor.cancelar_reserva("R1")
        self.assertEqual(self.sala.cupos_disponibles, 1)

    def test_16_procesar_reserva(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        self.gestor.confirmar_reserva("R1")
        self.assertEqual(self.gestor.procesar_reserva("R1").estado, EstadoReserva.PROCESADA)

    def test_17_rechazar_cancelacion_procesada(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        self.gestor.confirmar_reserva("R1")
        self.gestor.procesar_reserva("R1")
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.cancelar_reserva("R1")

    def test_18_no_permitir_procesar_pendiente(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.procesar_reserva("R1")

    def test_19_rechazar_reserva_duplicada(self):
        self.gestor.crear_reserva("R1", "C1", "S1", 1)
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.crear_reserva("R1", "C1", "S1", 2)

    def test_20_limite_de_duracion_sala(self):
        with self.assertRaises(DatosInvalidosError):
            self.sala.calcular_costo(13)

    def test_21_entrada_decimal_no_enteros(self):
        with self.assertRaises(DatosInvalidosError):
            self.asesoria.calcular_costo("2.5")

    def test_22_rechazo_valor_numerico_no_finito(self):
        with self.assertRaises(DatosInvalidosError):
            self.sala.calcular_costo(1, "NaN")

    def test_23_rechazo_parametro_vacio(self):
        with self.assertRaises(DatosInvalidosError):
            self.gestor.crear_reserva("", "C1", "S1", 1)

    def test_24_rechazo_servicio_incorrecto(self):
        with self.assertRaises(DatosInvalidosError):
            self.gestor.registrar_servicio("texto")


if __name__ == "__main__":
    unittest.main()
