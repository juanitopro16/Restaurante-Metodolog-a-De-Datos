# Sistema de Comandas — integración de Sprints 1 a 4

## Inicio

1. **Haz copia de seguridad** de `restaurante.db` antes de ejecutar.
2. Requiere Python 3.10+ y Tkinter (incluido habitualmente en Windows).
3. Ejecuta `python main.py` desde esta carpeta. No instales paquetes externos.
4. Inicia sesión con las cuentas de prueba ya existentes de la base de datos. Cambia contraseñas antes de uso real.
5. Usa `python -m unittest discover -p "prueba*.py" -v` para ejecutar pruebas. Las pruebas de integración usan bases temporales cuando así se programaron.

## Módulos por responsable y función

| Responsable | Sprint / tareas | Archivos | Función |
|---|---|---|---|
| Juan Antonio | Sprint 4 T45, T46, T51, T52 | `juan_sprint4.py` | Guarda pagos como ventas al cerrar mesa, suma ventas diarias, menú y mesas rediseñados |
| Said Jesús (tareas asignadas) | Sprint 4 T49, T50, T62, T64 | `said_sprint4.py` | Filtra pedidos pagados, muestra detalle, login y gestión de empleados |
| Javier Tadeo | Sprint 4 T47, T53, T54, T55 | `javier_sprint4.py`, `javier_t47_*.py` | Reportes entre fechas, cobros, tickets, panel de ventas |
| Aarón Mendoza | Sprint 4 T48, T59, T60, T61 | `aaron_sprint4.py` | Historial, edición de comandas, tarjetas cocina y tiempos |
| Patricio Cosaín | Sprint 4 T56, T57, T58, T63 | `pato_pantallas.py`, `estilos_sprint4.py` | Inventario, alertas, órdenes de compra, estilo compartido |

**Los módulos anteriores de Sprint 3 se mantienen:** `base_datos.py`, `javier_caja_proveedores.py`, `javier_pantallas.py`, `pato_almacen.py`, `sprint3_nuevo.py`, `sprint3_pantallas.py`.

## Flujo funcional

1. Said T62 → inicio de sesión, `main.py` conserva validación original.
2. Juan T51 → menú según `permisos.py`.
3. Juan T52 → consulta mesas; menú «Crear pedidos» abre gestión original.
4. Aarón T59 → crear/editar productos de pedido, T61 registra hora al enviarlo.
5. Aarón T60 → cocina muestra comandas por estado y tiempo transcurrido.
6. Javier T53/T54 → caja registra pago y presenta ticket con importes congelados.
7. Juan T45 → en «Consultar consumos y cerrar mesas» cierra mesa y registra venta.
8. Juan T46 / Javier T47 y T55 → resumen y reporte usando **fecha de cierre**.
9. Aarón T48 / Said T49-T50 → historial de pedidos cobrados y detalles.
10. Said T64 → alta, edición y desactivación de usuarios; Pato T56-T58 → almacén y compras.

## Cambios específicos de integración

- `main.py`: importa los cinco módulos, inicializa ventas y tiempo de envío; reemplaza pantallas por delegación y añade rutas de historial/reportes.
- `permisos.py`: habilita historial y reportes **solo a gerente y caja**.
- `sprint3_pantallas.py`: cambia únicamente la acción de cierre a `cerrar_mesa_t45`; dirige botón de caja al rediseño T53.
- `pato_pantallas.py`: versión de Pato para Sprint 4, que importa `estilos_sprint4.py`.
- Se conservó la base de datos original de Sprint 3 **como copia**, sin borrar datos.

## Riesgos y limitaciones a comprobar

- **T45:** pagos antiguos de una mesa que nunca se registraron en `ventas_cierre_s4` pueden asociarse erróneamente a un cierre posterior. Para una base con historial de producción, se necesita migración controlada antes de usar reportes.
- **T45:** el cierre requiere que todos los pedidos históricos asociados a esa mesa estén entregados y pagados. En bases con registros de prueba antiguos puede requerir depuración de datos en una copia.
- **T48/T50:** el total de un pago que agrupa varios pedidos **no es el total individual de cada pedido**; el historial muestra esa distinción.
- **T59/T60/T62/T64:** falta inspección manual visual en Windows; algunos widgets pueden requerir ajuste de tamaño.
- **T58:** el cambio de estado y recepción de compras sigue en la pantalla anterior del Sprint 3.
- **Seguridad:** las cuentas de demostración no son apropiadas para uso comercial real.

## Créditos

Las asignaciones de Sprint 4 indican **responsables de tarea**, no certifican autoría personal de cada línea. Los módulos de Juan y Said y la finalización de Javier fueron preparados con asistencia de IA; el código aportado por Aarón y Patricio se conservó, con adaptaciones de integración. Los comentarios identifican responsabilidad, sprint y finalidad.
