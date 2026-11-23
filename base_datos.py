# ================================================================
# RESPONSABILIDAD / MÓDULO: Equipo original | Sprints 1–2 | persistencia de usuarios, productos, mesas y pedidos
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
import hashlib
import os
import sqlite3
from permisos import obtener_roles

NOMBRE_BD = os.path.join(os.path.dirname(__file__), "restaurante.db")

# EXPLICACIÓN DEL SEGMENTO: Abre la base SQLite ubicada junto a los archivos del sistema.
def conectar():
    # Abre una conexión a la base SQLite.
    return sqlite3.connect(NOMBRE_BD)

# ================================================================
# SPRINT 1 - TAREA 2
# Nombre: Crear el registro de usuarios y guardar contraseñas protegidas
# Responsable: Javier Tadeo Jasso Vidaña
# ¿QUÉ HACE? Convierte contraseñas en hash y prepara las tablas.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Convierte una contraseña a un hash SHA-256 (solo demostración académica).
def hashear_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# EXPLICACIÓN DEL SEGMENTO: Crea tablas, migra columnas faltantes y agrega cuentas de demostración si no hay usuarios.
def inicializar_base_de_datos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1)""")
    columnas = [c[1] for c in cursor.execute("PRAGMA table_info(usuarios)")]
    if "nombre" in columnas and "nombre_completo" not in columnas:
        cursor.execute("ALTER TABLE usuarios RENAME COLUMN nombre TO nombre_completo")
    if "activo" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN activo INTEGER NOT NULL DEFAULT 1")

    cursor.execute("""CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
        categoria TEXT NOT NULL, descripcion TEXT DEFAULT '',
        precio REAL NOT NULL, disponible INTEGER NOT NULL DEFAULT 1)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS mesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, numero INTEGER UNIQUE NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Libre')""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, mesa_id INTEGER NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Borrador',
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(mesa_id) REFERENCES mesas(id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS detalle_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL, cantidad INTEGER NOT NULL,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id))""")
    # SPRINT 2 - TAREA 20 (Aarón Mendoza Rodríguez): si la base ya existía sin la
    # columna 'notas', se agrega con ALTER TABLE sin perder los registros actuales.
    columnas_detalle = [c[1] for c in cursor.execute("PRAGMA table_info(detalle_pedido)")]
    if "notas" not in columnas_detalle:
        cursor.execute("ALTER TABLE detalle_pedido ADD COLUMN notas TEXT DEFAULT ''")

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        pruebas = [
            ("Juan Gerente", "gerente1", "admin123", "gerente"),
            ("Carlos Mesero", "mesero1", "mesero123", "mesero"),
            ("Ana Cocina", "cocina1", "cocina123", "cocina"),
            ("Roberto Caja", "caja1", "caja123", "caja"),
            ("Lucia Almacen", "almacen1", "almacen123", "almacen")]
        for nombre, usuario, clave, rol in pruebas:
            cursor.execute("""INSERT INTO usuarios
                (nombre_completo, usuario, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, 1)""",
                (nombre, usuario, hashear_password(clave), rol))
    conexion.commit()
    conexion.close()

# ================================================================
# SPRINT 1 - TAREA 8
# Nombre: Crear el formulario para dar de alta a empleados
# Responsable: Said Jesús Echeverría Alcocer
# ¿QUÉ HACE? Valida y guarda los datos enviados desde el formulario.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Valida los datos y registra un empleado con su rol.
def registrar_usuario(nombre, usuario, password, rol):
    nombre, usuario, rol = nombre.strip(), usuario.strip(), rol.lower().strip()
    if not nombre or not usuario or not password:
        return False, "Completa todos los datos."
    if rol not in obtener_roles():
        return False, "Selecciona un puesto válido."
    conexion = conectar()
    try:
        conexion.execute("""INSERT INTO usuarios
            (nombre_completo, usuario, password_hash, rol, activo)
            VALUES (?, ?, ?, ?, 1)""",
            (nombre, usuario, hashear_password(password), rol))
        conexion.commit()
        return True, "Empleado registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "Ese nombre de usuario ya existe."
    finally:
        conexion.close()

# ================================================================
# SPRINT 1 - TAREA 3
# Nombre: Validar el usuario y la contraseña al ingresar
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Comprueba usuario, contraseña y que la cuenta esté activa.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Verifica usuario, contraseña y estado activo antes de iniciar sesión.
def validar_credenciales(usuario, password):
    conexion = conectar()
    fila = conexion.execute("""SELECT id, nombre_completo, usuario, password_hash, rol
        FROM usuarios WHERE usuario = ? AND activo = 1""", (usuario.strip(),)).fetchone()
    conexion.close()
    if fila is None or hashear_password(password) != fila[3]:
        return None
    return {"id": fila[0], "nombre": fila[1], "usuario": fila[2], "rol": fila[4]}

# ================================================================
# SPRINT 2 - TAREA 9
# Nombre: Permitir modificar los datos y el puesto de un empleado
# Responsable: Juan Antonio Ibarra Hernández
# ¿QUÉ HACE? Consulta empleados activos y actualiza nombre y puesto.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Consulta los empleados para la tabla de administración.
def listar_empleados():
    c = conectar()
    filas = c.execute("SELECT id, nombre_completo, usuario, rol, activo FROM usuarios ORDER BY id").fetchall()
    c.close()
    return filas

# EXPLICACIÓN DEL SEGMENTO: Actualiza nombre y rol del empleado seleccionado.
def modificar_empleado(empleado_id, nombre, rol):
    if not nombre.strip() or rol.lower().strip() not in obtener_roles():
        return False, "Revisa el nombre y el puesto."
    c = conectar()
    c.execute("UPDATE usuarios SET nombre_completo=?, rol=? WHERE id=?",
              (nombre.strip(), rol.lower().strip(), empleado_id))
    c.commit()
    c.close()
    return True, "Empleado actualizado."

# ================================================================
# SPRINT 2 - TAREA 10
# Nombre: Permitir desactivar el acceso de empleados que ya no trabajen
# Responsable: Juan Antonio Ibarra Hernández
# ¿QUÉ HACE? Desactiva la cuenta sin borrar el registro del empleado.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Revoca el acceso sin borrar su historial.
def desactivar_empleado(empleado_id):
    c = conectar()
    c.execute("UPDATE usuarios SET activo=0 WHERE id=?", (empleado_id,))
    c.commit()
    c.close()

# ================================================================
# SPRINT 4 - T64 | RESPONSABLE DE TAREA: Said Jesús
# INTEGRACIÓN: corrección de administración de usuarios con asistencia de IA.
# FUNCIÓN: Reactivar el acceso de una cuenta previamente desactivada.
# No crea usuarios nuevos, no modifica contraseñas ni elimina registros.
# ================================================================
def activar_empleado(empleado_id):
    """Activa un empleado existente y devuelve (éxito, mensaje)."""
    try:
        empleado_id = int(empleado_id)
    except (TypeError, ValueError):
        return False, "Identificador de empleado inválido."
    if empleado_id <= 0:
        return False, "Identificador de empleado inválido."
    conexion = conectar()
    try:
        fila = conexion.execute("SELECT activo FROM usuarios WHERE id=?", (empleado_id,)).fetchone()
        if fila is None:
            return False, "El empleado no existe."
        if fila[0]:
            return False, "El empleado ya está activo."
        conexion.execute("UPDATE usuarios SET activo=1 WHERE id=?", (empleado_id,))
        conexion.commit()
        return True, "Empleado reactivado. Ya puede iniciar sesión."
    finally:
        conexion.close()

# ================================================================
# SPRINT 2 - TAREA 12
# Nombre: Registrar productos con nombre, categoría y precio
# Responsable: Javier Tadeo Jasso Vidaña
# ¿QUÉ HACE? Guarda un producto nuevo en el catálogo.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Valida precio, nombre y categoría; guarda un producto.
def registrar_producto(nombre, categoria, descripcion, precio):
    if not nombre.strip() or not categoria.strip():
        return False, "Escribe nombre y categoría."
    try:
        precio = float(precio)
        if precio < 0: raise ValueError
    except ValueError:
        return False, "El precio debe ser un número igual o mayor a cero."
    c = conectar()
    c.execute("""INSERT INTO productos(nombre,categoria,descripcion,precio,disponible)
                 VALUES(?,?,?,?,1)""",
              (nombre.strip(), categoria.strip(), descripcion.strip(), precio))
    c.commit()
    c.close()
    return True, "Producto registrado."

# EXPLICACIÓN DEL SEGMENTO: Recupera el catálogo completo o solo los disponibles.
def listar_productos(solo_disponibles=False):
    c = conectar()
    sql = "SELECT id,nombre,categoria,descripcion,precio,disponible FROM productos"
    if solo_disponibles: sql += " WHERE disponible=1"
    filas = c.execute(sql + " ORDER BY nombre").fetchall()
    c.close()
    return filas

# ================================================================
# SPRINT 2 - TAREA 13
# Nombre: Permitir cambiar el nombre, descripción y precio de los productos
# Responsable: Aarón Mendoza Rodríguez
# ¿QUÉ HACE? Actualiza los datos del producto seleccionado.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Actualiza nombre, descripción y precio.
def modificar_producto(producto_id, nombre, descripcion, precio):
    if not nombre.strip(): return False, "El nombre no puede quedar vacío."
    try:
        precio = float(precio)
        if precio < 0: raise ValueError
    except ValueError:
        return False, "Precio no válido."
    c = conectar()
    c.execute("UPDATE productos SET nombre=?, descripcion=?, precio=? WHERE id=?",
              (nombre.strip(), descripcion.strip(), precio, producto_id))
    c.commit()
    c.close()
    return True, "Producto actualizado."

# ================================================================
# SPRINT 2 - TAREA 14
# Nombre: Marcar los productos como disponibles o agotados
# Responsable: Javier Tadeo Jasso Vidaña
# ¿QUÉ HACE? Cambia el indicador de disponibilidad del producto.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Marca el producto como disponible o agotado.
def cambiar_disponibilidad(producto_id, disponible):
    c = conectar()
    c.execute("UPDATE productos SET disponible=? WHERE id=?",
              (1 if disponible else 0, producto_id))
    c.commit()
    c.close()

# ================================================================
# SPRINT 2 - TAREA 16
# Nombre: Registrar las mesas con su número correspondiente
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Guarda un número único para cada mesa.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Crea una mesa con número único y estado Libre.
def registrar_mesa(numero):
    try:
        numero = int(numero)
        if numero <= 0: raise ValueError
    except ValueError:
        return False, "El número debe ser un entero positivo."
    c = conectar()
    try:
        c.execute("INSERT INTO mesas(numero,estado) VALUES(?,'Libre')", (numero,))
        c.commit()
        return True, "Mesa registrada."
    except sqlite3.IntegrityError:
        return False, "Ese número de mesa ya existe."
    finally:
        c.close()

# ================================================================
# SPRINT 2 - TAREA 17
# Nombre: Indicar cuáles mesas están libres y cuáles ocupadas
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Devuelve las mesas y su estado para mostrarlos en pantalla.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Devuelve número y estado de las mesas.
def listar_mesas():
    c = conectar()
    filas = c.execute("SELECT id,numero,estado FROM mesas ORDER BY numero").fetchall()
    c.close()
    return filas

# ================================================================
# SPRINT 2 - TAREA 18
# Nombre: Crear un pedido nuevo y relacionarlo con una mesa
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Crea un pedido Borrador y marca la mesa como ocupada.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Crea un borrador asociado a una mesa libre y la ocupa.
def crear_pedido(mesa_id):
    c = conectar()
    cur = c.cursor()
    mesa = cur.execute("SELECT estado FROM mesas WHERE id=?", (mesa_id,)).fetchone()
    if mesa is None or mesa[0] != "Libre":
        c.close()
        return False, "La mesa no existe o está ocupada.", None
    cur.execute("INSERT INTO pedidos(mesa_id,estado) VALUES(?,'Borrador')", (mesa_id,))
    pedido_id = cur.lastrowid
    cur.execute("UPDATE mesas SET estado='Ocupada' WHERE id=?", (mesa_id,))
    c.commit()
    c.close()
    return True, "Pedido creado.", pedido_id

# ================================================================
# SPRINT 2 - TAREA 19
# Nombre: Elegir platillos y bebidas con sus cantidades
# Responsable: Aarón Mendoza Rodríguez
# ¿QUÉ HACE? Agrega productos disponibles y sus cantidades al pedido.
# (T20: ahora también guarda una nota opcional, por ejemplo "sin cebolla")
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Agrega al borrador un producto disponible con cantidad y nota.
def agregar_producto_pedido(pedido_id, producto_id, cantidad, notas=""):
    try:
        cantidad = int(cantidad)
        if cantidad <= 0: raise ValueError
    except ValueError:
        return False, "La cantidad debe ser un entero mayor que cero."
    notas = (notas or "").strip()
    c = conectar()
    cur = c.cursor()
    pedido = cur.execute("SELECT estado FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    producto = cur.execute("SELECT disponible FROM productos WHERE id=?", (producto_id,)).fetchone()
    if pedido is None or pedido[0] != "Borrador":
        c.close()
        return False, "El pedido no está disponible para agregar productos."
    if producto is None or producto[0] != 1:
        c.close()
        return False, "El producto está agotado o no existe."
    cur.execute("INSERT INTO detalle_pedido(pedido_id,producto_id,cantidad,notas) VALUES(?,?,?,?)",
                (pedido_id, producto_id, cantidad, notas))
    c.commit()
    c.close()
    return True, "Producto agregado."

# ================================================================
# SPRINT 2 - TAREA 20
# Nombre: Permitir corregir o quitar productos antes de enviarlos
# Responsable: Aarón Mendoza Rodríguez
# ¿QUÉ HACE? Devuelve los renglones del pedido (con su id y nota) y permite
#            modificarlos o quitarlos mientras el pedido siga en Borrador.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Consulta los renglones con identificador, precio, cantidad y nota.
def listar_detalle_pedido(pedido_id):
    # Cada fila: (id_del_renglon, nombre, cantidad, precio, nota)
    c = conectar()
    filas = c.execute("""SELECT dp.id, p.nombre, dp.cantidad, p.precio, COALESCE(dp.notas, '')
        FROM detalle_pedido dp JOIN productos p ON p.id=dp.producto_id
        WHERE dp.pedido_id=? ORDER BY dp.id""", (pedido_id,)).fetchall()
    c.close()
    return filas

def _estado_pedido_de_detalle(cursor, detalle_id):
    # Devuelve el estado del pedido al que pertenece un renglón (o None si no existe).
    fila = cursor.execute("""SELECT pe.estado FROM detalle_pedido dp
        JOIN pedidos pe ON pe.id=dp.pedido_id WHERE dp.id=?""", (detalle_id,)).fetchone()
    return None if fila is None else fila[0]

# EXPLICACIÓN DEL SEGMENTO: Cambia cantidad y nota solo cuando el pedido es borrador.
def modificar_detalle_pedido(detalle_id, cantidad, notas=""):
    try:
        cantidad = int(cantidad)
        if cantidad <= 0: raise ValueError
    except ValueError:
        return False, "La cantidad debe ser un entero mayor que cero."
    notas = (notas or "").strip()
    c = conectar()
    cur = c.cursor()
    estado = _estado_pedido_de_detalle(cur, detalle_id)
    if estado is None:
        c.close()
        return False, "Ese producto ya no está en el pedido."
    if estado != "Borrador":
        c.close()
        return False, "El pedido ya fue enviado a cocina y no se puede modificar."
    cur.execute("UPDATE detalle_pedido SET cantidad=?, notas=? WHERE id=?",
                (cantidad, notas, detalle_id))
    c.commit()
    c.close()
    return True, "Producto actualizado."

# EXPLICACIÓN DEL SEGMENTO: Elimina un renglón únicamente de pedidos en borrador.
def quitar_producto_pedido(detalle_id):
    c = conectar()
    cur = c.cursor()
    estado = _estado_pedido_de_detalle(cur, detalle_id)
    if estado is None:
        c.close()
        return False, "Ese producto ya no está en el pedido."
    if estado != "Borrador":
        c.close()
        return False, "El pedido ya fue enviado a cocina y no se puede modificar."
    cur.execute("DELETE FROM detalle_pedido WHERE id=?", (detalle_id,))
    c.commit()
    c.close()
    return True, "Producto quitado del pedido."

# EXPLICACIÓN DEL SEGMENTO: Permite retomar un borrador desde la mesa.
def obtener_pedido_borrador_mesa(mesa_id):
    # Devuelve el id del pedido en Borrador de una mesa, o None si no tiene.
    c = conectar()
    fila = c.execute("""SELECT id FROM pedidos WHERE mesa_id=? AND estado='Borrador'
        ORDER BY id DESC LIMIT 1""", (mesa_id,)).fetchone()
    c.close()
    return None if fila is None else fila[0]

# ================================================================
# SPRINT 2 - TAREA 21
# Nombre: Guardar el pedido y enviarlo a la sección de cocina
# Responsable: Aarón Mendoza Rodríguez
# ¿QUÉ HACE? Valida el pedido y cambia su estado de Borrador a Pendiente
#            (sin crear otro pedido) para que cocina pueda consultarlo.
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Valida que haya productos y cambia Borrador a Pendiente.
def enviar_pedido_cocina(pedido_id):
    c = conectar()
    cur = c.cursor()
    pedido = cur.execute("SELECT estado FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if pedido is None:
        c.close()
        return False, "El pedido no existe."
    if pedido[0] != "Borrador":
        c.close()
        return False, f"Este pedido ya no está en borrador (estado actual: {pedido[0]})."
    total = cur.execute("SELECT COUNT(*) FROM detalle_pedido WHERE pedido_id=?", (pedido_id,)).fetchone()[0]
    if total == 0:
        c.close()
        return False, "El pedido está vacío. Agrega al menos un producto antes de enviarlo."
    # La condición AND estado='Borrador' evita que se envíe dos veces.
    cur.execute("UPDATE pedidos SET estado='Pendiente' WHERE id=? AND estado='Borrador'", (pedido_id,))
    c.commit()
    c.close()
    return True, "Pedido enviado a cocina. Estado: Pendiente."

# ================================================================
# SPRINT 2 - TAREA 22
# Nombre: Mostrar los pedidos pendientes en cocina
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Obtiene folio y mesa de las comandas pendientes.
def listar_pedidos_pendientes():
    c = conectar()
    try:
        return c.execute("""SELECT p.id, m.numero FROM pedidos AS p
            JOIN mesas AS m ON m.id = p.mesa_id
            WHERE p.estado = 'Pendiente' ORDER BY p.id""").fetchall()
    finally:
        c.close()


# ================================================================
# SPRINT 2 - TAREA 24
# Nombre: Permitir marcar un pedido como En preparación
# Responsable: Javier Tadeo Jasso Vidaña
# ================================================================
# EXPLICACIÓN DEL SEGMENTO: Actualiza Pendiente a En preparación en una sola sentencia condicionada.
def marcar_pedido_en_preparacion(pedido_id):
    c = conectar()
    try:
        with c:
            # Validar y actualizar en una sola operación evita tomarlo dos veces.
            cambio = c.execute("""UPDATE pedidos SET estado = 'En preparación'
                WHERE id = ? AND estado = 'Pendiente'""", (pedido_id,))
            if cambio.rowcount != 1:
                return False, "El pedido no existe o ya no está pendiente."
        return True, f"Pedido #{pedido_id} marcado como En preparación."
    finally:
        c.close()
