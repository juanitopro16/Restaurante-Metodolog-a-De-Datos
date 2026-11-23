# Corrección de T64 — activar y desactivar empleados

**Responsable de la tarea:** Said Jesús. **Sprint:** 4. **Integración y corrección:** realizada con asistencia de IA.

## Cambios

- `base_datos.py`: nueva función `activar_empleado(empleado_id)`. Comprueba que la cuenta exista, que esté inactiva y actualiza exclusivamente `usuarios.activo` a `1`. No cambia contraseñas ni elimina registros.
- `said_sprint4.py`: en `mostrar_empleados_said(app)`, el botón de acceso cambia de **Desactivar** a **Activar** según el registro seleccionado. Solicita confirmación, actualiza la tabla y conserva la selección.
- El gerente no puede desactivar su propia cuenta desde esta pantalla.
- La desactivación no equivale al fin de turno.

## Cómo reactivar a Pato

1. Inicia sesión con `gerente1`.
2. Entra a **Empleados y usuarios**.
3. Selecciona la fila de Pato (`lavolsa`), que debe mostrar **Activo: No**.
4. Presiona **Activar** y confirma.
5. Verifica que la columna cambie a **Sí**. Pato podrá iniciar sesión con su contraseña anterior.

## Ejecución

Desde la carpeta que contiene `main.py`:

```bash
python main.py
```

**Importante:** cierra la versión anterior antes de abrir esta; trabaja siempre en la carpeta corregida y no mezcles archivos de ambas versiones. Se conservó una copia de `restaurante.db` tal como estaba en la entrega anterior. Realiza un respaldo antes de trabajar con datos importantes.

## Validación

- Compilación de archivos Python: correcta.
- Prueba con SQLite temporal: desactivar, impedir inicio de sesión, activar, permitir inicio de sesión, rechazar reactivación duplicada y empleado inexistente: correcta.
- Pruebas existentes ejecutadas sin errores reportados.
- **Pendiente:** verificación manual de la pantalla en Windows.
