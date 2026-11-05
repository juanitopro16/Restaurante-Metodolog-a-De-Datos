import hashlib
import os
import sqlite3

from permisos import obtener_roles

# El archivo de la base de datos se crea dentro de esta carpeta.
NOMBRE_BD = os.path.join(os.path.dirname(__file__), "restaurante.db")


# ================================================================
# SPRINT 1 - TAREA E1-2
# Nombre: Crear el registro de usuarios y guardar contraseñas protegidas
# Responsable: Javier Tadeo Jasso Vidaña
# ================================================================

# Convierte la contraseña en un hash antes de guardarla en la base de datos.
def hashear_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Crea la tabla de usuarios y agrega cuentas de prueba la primera vez.
def inicializar_base_de_datos():
    conexion = sqlite3.connect(NOMBRE_BD)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # Si existe una base anterior, se conserva y se cambia el nombre de la columna.
    columnas = [dato[1] for dato in cursor.execute("PRAGMA table_info(usuarios)")]
    if "nombre" in columnas and "nombre_completo" not in columnas:
        cursor.execute(
            "ALTER TABLE usuarios RENAME COLUMN nombre TO nombre_completo"
        )

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    cantidad = cursor.fetchone()[0]

    # Estas cuentas sirven para probar los cinco tipos de usuario.
    if cantidad == 0:
        usuarios_prueba = [
            ("Juan Gerente", "gerente1", "admin123", "gerente"),
            ("Carlos Mesero", "mesero1", "mesero123", "mesero"),
            ("Ana Cocina", "cocina1", "cocina123", "cocina"),
            ("Roberto Caja", "caja1", "caja123", "caja"),
            ("Lucia Almacen", "almacen1", "almacen123", "almacen"),
        ]

        for nombre, usuario, password, rol in usuarios_prueba:
            cursor.execute(
                """INSERT INTO usuarios
                   (nombre_completo, usuario, password_hash, rol)
                   VALUES (?, ?, ?, ?)""",
                (nombre, usuario, hashear_password(password), rol),
            )

    conexion.commit()
    conexion.close()


# ================================================================
# SPRINT 2 - TAREA E1-8
# Nombre: Crear el formulario para dar de alta a empleados
# Responsable: Said Jesús Echeverría Alcocer
# ================================================================

# Esta función guarda los datos que se escriben en el formulario de empleados.
def registrar_usuario(nombre, usuario, password, rol):
    nombre = nombre.strip()
    usuario = usuario.strip()
    rol = rol.lower().strip()

    if nombre == "" or usuario == "" or password == "":
        return False, "Completa todos los datos."

    if rol not in obtener_roles():
        return False, "Selecciona un puesto válido."

    conexion = sqlite3.connect(NOMBRE_BD)

    try:
        conexion.execute(
            """INSERT INTO usuarios
               (nombre_completo, usuario, password_hash, rol)
               VALUES (?, ?, ?, ?)""",
            (nombre, usuario, hashear_password(password), rol),
        )
        conexion.commit()
        return True, "Empleado registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "Ese nombre de usuario ya existe."
    finally:
        conexion.close()


# ================================================================
# SPRINT 1 - TAREA E1-3
# Nombre: Validar el usuario y la contraseña al ingresar
# Responsable: Patricio Cosaín Torres
# ================================================================

# Busca el usuario y revisa si la contraseña coincide con la guardada.
def validar_credenciales(usuario, password):
    conexion = sqlite3.connect(NOMBRE_BD)
    cursor = conexion.cursor()

    cursor.execute(
        """SELECT id, nombre_completo, usuario, password_hash, rol
           FROM usuarios WHERE usuario = ?""",
        (usuario.strip(),),
    )
    registro = cursor.fetchone()
    conexion.close()

    if registro is None:
        return None

    if hashear_password(password) != registro[3]:
        return None

    # Se regresan los datos que necesita la pantalla después de iniciar sesión.
    datos_usuario = {
        "id": registro[0],
        "nombre": registro[1],
        "usuario": registro[2],
        "rol": registro[4],
    }
    return datos_usuario
