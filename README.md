# Sistema integral de gestión de clientes, servicios y reservas

Proyecto en Python para **Software FJ**. Permite gestionar clientes, servicios y reservas, sin motor de base de datos. Toda la información del negocio permanece en memoria durante la ejecución. El archivo `logs/eventos.log` almacena exclusivamente eventos y errores.

## Requisitos

- Python 3.10 o posterior.
- No requiere instalar paquetes externos.

## Ejecutar

Abra una terminal en la carpeta principal del proyecto.

```bash
python main.py
```

La aplicación mostrará el menú para registrar clientes, consultar servicios, crear reservas, confirmarlas, procesarlas, cancelarlas y cotizar costos. Los servicios iniciales se cargan automáticamente para las pruebas de menú.

## Ejecutar las 20 operaciones demostrativas

```bash
python main.py --demo
```

Se prueban clientes válidos e inválidos, registros duplicados, creación correcta e incorrecta de servicios, confirmación de reservas, falta de disponibilidad, procesamiento, cancelación y recuperación posterior a errores. Cada resultado se muestra en consola y los eventos o errores quedan registrados en `logs/eventos.log`.

## Ejecutar las 24 pruebas unitarias

```bash
python -m unittest discover -s tests -v
```

## Estructura

```text
software_fj/
├── main.py                     Menú y demostración
├── software_fj/
│   ├── __init__.py
│   ├── entidades.py            Clase abstracta Entidad y clase Cliente
│   ├── servicios.py            Servicio y sus tres especializaciones
│   ├── reservas.py             Reserva y estados
│   ├── gestion.py              Administrador de datos en memoria y logs
│   ├── errores.py              Excepciones personalizadas
│   └── validacion.py           Validadores de entradas
├── tests/
│   └── test_sistema.py         Pruebas unitarias
├── logs/
│   └── eventos.log             Registro automático
└── README.md                   Documentación
```

## Diseño orientado a objetos

- **Abstracción:** `Entidad` y `Servicio` son clases abstractas.
- **Herencia:** `Cliente`, `Reserva` y los tres tipos de servicio derivan de clases abstractas.
- **Polimorfismo:** cada servicio redefine su costo base, la validación de duración y su descripción.
- **Encapsulación:** `Cliente` protege los datos de contacto; la modificación del correo se hace mediante un método validado.
- **Sobrecarga expresada en tipos:** `Servicio.calcular_costo` declara variantes con `@overload` y recibe parámetros opcionales para impuesto y descuento. En Python la implementación efectiva es una función con argumentos opcionales, no un despacho automático por firma.
- **Excepciones:** tipos propios de error, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from ...`).

## Reglas de reservas

Una reserva inicia **Pendiente**. Puede pasar a **Confirmada** si hay cupos y luego a **Procesada**. Las reservas pendientes y confirmadas pueden **Cancelarse**; al cancelar una confirmada se libera el cupo. Una reserva procesada no puede cancelarse. El sistema verifica que los registros existan, no estén duplicados y que los datos ingresados sean coherentes.

### Nota sobre disponibilidad

Los cupos se modelan como disponibilidad simultánea simplificada. No se incluyen fechas u horarios ni persistencia de datos, porque el alcance solicitado se centra en los principios orientados a objetos y la gestión de excepciones. Los cupos de una reserva procesada permanecen ocupados durante la sesión, y solamente la cancelación previa al procesamiento los libera.

## Para publicar en GitHub

1. Cree un repositorio nuevo en GitHub.
2. Suba los archivos de esta carpeta (manteniendo sus subcarpetas).
3. Incluya el enlace del repositorio en la entrega académica.
4. Compruebe que otra persona pueda clonar el repositorio y ejecutar las dos instrucciones de prueba.
