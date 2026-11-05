# Sistema de Comandas para Restaurante

Proyecto escolar de la materia Metodologías Ágiles y Desarrollo de Software.

El programa está hecho con Python, Tkinter y SQLite. No necesita instalar librerías externas.

## Cómo ejecutarlo

1. Tener Python instalado.
2. Abrir una terminal dentro de esta carpeta.
3. Ejecutar:

```bash
python main.py
```

La base de datos `restaurante.db` se crea automáticamente al iniciar el programa.

## Cuentas para probar

| Puesto | Usuario | Contraseña |
|---|---|---|
| Gerente | `gerente1` | `admin123` |
| Mesero | `mesero1` | `mesero123` |
| Cocina | `cocina1` | `cocina123` |
| Caja | `caja1` | `caja123` |
| Almacén | `almacen1` | `almacen123` |

## Archivos

- `main.py`: ventanas, inicio y cierre de sesión, menús y formulario de empleados.
- `base_datos.py`: tabla de usuarios, registro y validación.
- `permisos.py`: puestos y opciones de cada puesto.
- `.gitignore`: evita subir la base de datos y archivos temporales.

## Tareas y responsables

### Sprint 1

| Tarea | Nombre | Responsable |
|---|---|---|
| E1-1 | Diseñar la pantalla de inicio de sesión | Juan Antonio Ibarra Hernández |
| E1-2 | Crear el registro de usuarios y guardar contraseñas protegidas | Javier Tadeo Jasso Vidaña |
| E1-3 | Validar el usuario y la contraseña al ingresar | Patricio Cosaín Torres |
| E1-4 | Permitir cerrar sesión y volver al acceso | Said Jesús Echeverría Alcocer |
| E1-5 | Definir los permisos de mesero, cocina, caja, almacén y gerente | Juan Antonio Ibarra Hernández |

### Sprint 2

| Tarea | Nombre | Responsable |
|---|---|---|
| E1-6 | Crear un menú principal diferente para cada puesto | Aaron Mendoza Rodríguez |
| E1-7 | Bloquear las funciones que no correspondan al puesto | Patricio Cosaín Torres |
| E1-8 | Crear el formulario para dar de alta a empleados | Said Jesús Echeverría Alcocer |

Los nombres de los responsables corresponden a la distribución de tareas del equipo.

## Qué incluye

- Pantalla para iniciar sesión.
- Base de datos local de usuarios.
- Registro de empleados.
- Validación del usuario y la contraseña.
- Cierre de sesión.
- Menús diferentes según el puesto.
- Revisión de permisos antes de abrir una opción.
- Formulario para dar de alta empleados.

Las opciones de mesas, comandas, pagos, inventario y reportes se muestran como ejemplos de menú. Sus procesos completos pueden agregarse en otras tareas del backlog.

## Nota sobre las contraseñas

Para esta práctica escolar se usa SHA-256 para guardar un hash de la contraseña. Es una demostración sencilla y no se debe usar como protección de contraseñas en un sistema real.
