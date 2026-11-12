"""Punto de entrada: menú interactivo y simulación de operaciones."""
import argparse
from collections.abc import Callable
from typing import Any

from software_fj import (AlquilerEquipo, AsesoriaEspecializada, GestorReservas,
                         ReservaSala)
from software_fj.errores import ErrorSistema


def iniciar_servicios(gestor: GestorReservas) -> None:
    """Carga un catálogo inicial para facilitar las pruebas de consola."""
    gestor.registrar_servicio(ReservaSala("S01", "Sala de reuniones", 50000, 12, 2))
    gestor.registrar_servicio(AlquilerEquipo("S02", "Portátil", 35000, 2))
    gestor.registrar_servicio(AsesoriaEspecializada("S03", "Consultoría técnica", "Sistemas", 80000, 2))


def ejecutar_demostracion() -> bool:
    """Simula 20 operaciones; registra errores sin detener la ejecución."""
    gestor = GestorReservas()
    resultados: list[bool] = []

    def ejecutar(etiqueta: str, accion: Callable[[], Any], debe_fallar: bool = False) -> None:
        numero = len(resultados) + 1
        print(f"\n{numero:02d}. {etiqueta}")
        # Los errores esperados se registran y se continúa con la operación siguiente.
        try:
            resultado = accion()
        except (ErrorSistema, ValueError, TypeError) as exc:
            gestor.logger.error("Operación %02d fallida: %s: %s", numero, type(exc).__name__, exc)
            es_correcta = debe_fallar
            print(f"   Error controlado: {exc}")
        except Exception:
            gestor.logger.exception("Operación %02d produjo un error inesperado", numero)
            es_correcta = False
            print("   Se produjo un error inesperado; se registró en el log.")
        else:
            es_correcta = not debe_fallar
            if hasattr(resultado, "describir"):
                print(f"   {resultado.describir()}")
            else:
                print(f"   Resultado: {resultado}")
        finally:
            resultados.append(es_correcta)
            print(f"   Verificación: {'CORRECTA' if es_correcta else 'NO SUPERADA'}")

    ejecutar("Registrar cliente válido A", lambda: gestor.registrar_cliente("C01", "Ana Ejemplo", "ana@example.com", "3001234567"))
    ejecutar("Registrar cliente válido B", lambda: gestor.registrar_cliente("C02", "Luis Ejemplo", "luis@example.com", "3109876543"))
    ejecutar("Rechazar correo inválido", lambda: gestor.registrar_cliente("C03", "Error Ejemplo", "correo-no-valido", "3001234567"), True)
    ejecutar("Rechazar cliente duplicado", lambda: gestor.registrar_cliente("C01", "Otra Persona", "otra@example.com", "3001234567"), True)
    ejecutar("Registrar sala", lambda: gestor.registrar_servicio(ReservaSala("S01", "Sala principal", 50000, 10)))
    ejecutar("Registrar equipo", lambda: gestor.registrar_servicio(AlquilerEquipo("S02", "Proyector", 35000, 1)))
    ejecutar("Registrar asesoría", lambda: gestor.registrar_servicio(AsesoriaEspecializada("S03", "Asesoría Python", "Programación", 80000)))
    ejecutar("Rechazar servicio con tarifa negativa", lambda: gestor.registrar_servicio(ReservaSala("S04", "Sala inválida", -100, 5)), True)
    ejecutar("Crear reserva válida de sala", lambda: gestor.crear_reserva("R01", "C01", "S01", 2, 19, 10))
    ejecutar("Confirmar reserva de sala", lambda: gestor.confirmar_reserva("R01"))
    ejecutar("Rechazar reserva sin cliente existente", lambda: gestor.crear_reserva("R02", "C99", "S01", 1), True)
    ejecutar("Rechazar duración inválida", lambda: gestor.crear_reserva("R03", "C01", "S01", -2), True)
    ejecutar("Crear reserva válida de equipo", lambda: gestor.crear_reserva("R04", "C02", "S02", 3))
    ejecutar("Confirmar reserva de equipo", lambda: gestor.confirmar_reserva("R04"))
    ejecutar("Crear segunda reserva del mismo equipo", lambda: gestor.crear_reserva("R05", "C01", "S02", 1))
    ejecutar("Rechazar confirmación sin disponibilidad", lambda: gestor.confirmar_reserva("R05"), True)
    ejecutar("Procesar la reserva de sala", lambda: gestor.procesar_reserva("R01"))
    ejecutar("Rechazar cancelación de reserva procesada", lambda: gestor.cancelar_reserva("R01"), True)
    ejecutar("Cancelar reserva confirmada de equipo", lambda: gestor.cancelar_reserva("R04"))
    ejecutar("Confirmar reserva tras recuperar cupo", lambda: gestor.confirmar_reserva("R05"))

    correctas = sum(resultados)
    print(f"\nRESULTADO: {correctas}/{len(resultados)} operaciones verificadas correctamente.")
    print("Los errores y los eventos quedaron registrados en logs/eventos.log.")
    return correctas == len(resultados)


def menu() -> None:
    gestor = GestorReservas()
    iniciar_servicios(gestor)
    opciones = """\nSOFTWARE FJ - GESTIÓN DE RESERVAS
1. Registrar cliente
2. Ver servicios
3. Crear reserva
4. Confirmar reserva
5. Procesar reserva
6. Cancelar reserva
7. Ver clientes
8. Ver reservas
9. Cotizar servicio
0. Salir\n"""
    while True:
        try:
            print(opciones)
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "0":
                print("Sesión finalizada. Los datos en memoria se descartan.")
                return
            if opcion == "1":
                elemento = gestor.registrar_cliente(input("Identificación: "), input("Nombre: "),
                                                   input("Correo: "), input("Teléfono: "))
            elif opcion == "2":
                for servicio in gestor.servicios:
                    print(servicio.describir())
                continue
            elif opcion == "3":
                elemento = gestor.crear_reserva(input("ID de reserva: "), input("ID de cliente: "),
                                               input("ID de servicio: "), input("Duración (entera): "),
                                               input("Impuesto % (0 si no aplica): "),
                                               input("Descuento % (0 si no aplica): "))
            elif opcion == "4":
                elemento = gestor.confirmar_reserva(input("ID de reserva: "))
            elif opcion == "5":
                elemento = gestor.procesar_reserva(input("ID de reserva: "))
            elif opcion == "6":
                elemento = gestor.cancelar_reserva(input("ID de reserva: "))
            elif opcion == "7":
                for cliente in gestor.clientes:
                    print(cliente.describir())
                continue
            elif opcion == "8":
                for reserva in gestor.reservas:
                    print(reserva.describir())
                continue
            elif opcion == "9":
                servicio = gestor.obtener_servicio(input("ID de servicio: "))
                costo = servicio.calcular_costo(input("Duración: "), input("Impuesto %: "),
                                                input("Descuento %: "))
                print(f"Cotización: ${costo}")
                continue
            else:
                print("Opción no reconocida.")
                continue
            print(elemento.describir())
        except (ErrorSistema, ValueError, TypeError) as exc:
            gestor.logger.error("Error en menú: %s: %s", type(exc).__name__, exc)
            print(f"No se pudo completar la operación: {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\nSesión finalizada.")
            return
        except Exception:
            gestor.logger.exception("Error inesperado en menú")
            print("Se presentó un error no previsto. Consulte logs/eventos.log.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sistema de gestión de Software FJ")
    parser.add_argument("--demo", action="store_true", help="Ejecutar 20 operaciones de demostración")
    argumentos = parser.parse_args()
    if argumentos.demo:
        raise SystemExit(0 if ejecutar_demostracion() else 1)
    menu()
