# ================================================================
# RESPONSABILIDAD / MÓDULO: Patricio Cosaín | Sprint 3 | movimientos, inventario y órdenes de compra
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""SPRINT 3 | Patricio Cosaín Torres: T39, T40, T42 y T43 (almacén y compras).
Módulo independiente: usa la conexión del equipo (base_datos.conectar) y NO
reemplaza ni borra funciones de los Sprints 1 y 2 ni de otros compañeros.

Dependencias:
  - Said (T35-T38): tabla `insumos` (existencia, unidad, mínimo) y tabla
    `movimientos_inventario`. Si Said ya las creó con estos nombres, aquí solo
    se agregan las columnas que falten; no se crea una segunda tabla de insumos.
  - Javier (T41): tabla `proveedores_javier` (la usa T43).
  - Aarón (T44): recibirá las órdenes de compra creadas en T43.
"""
import sqlite3
from decimal import Decimal, InvalidOperation
from base_datos import conectar

MOTIVOS_SALIDA = ("Uso", "Desperdicio")


def _cantidad(valor):
    """Convierte el texto capturado en un número positivo (máx. 3 decimales).
    Devuelve float o lanza ValueError con un mensaje para la pantalla."""
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
        if not numero.is_finite() or numero <= 0:
            raise ValueError
        return float(round(numero, 3))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("La cantidad debe ser un número mayor que cero.")


def _redondear(valor):
    # Evita mostrar cosas como 5.999999999 después de restar flotantes.
    return round(float(valor), 3)


def _formato(valor):
    """Muestra 6 en lugar de 6.0 y 2.5 en lugar de 2.500."""
    valor = _redondear(valor)
    return str(int(valor)) if valor == int(valor) else f"{valor:g}"


# ================================================================
# SPRINT 3 - PREPARACIÓN DE TABLAS (T39, T40, T42, T43)
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Crea solo las tablas que falten. CREATE TABLE IF NOT EXISTS
#            conserva los datos ya guardados.
# ================================================================
def preparar_tablas_pato():
    with conectar() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            unidad TEXT NOT NULL DEFAULT 'pieza',
            existencia REAL NOT NULL DEFAULT 0,
            minimo REAL NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id INTEGER NOT NULL REFERENCES insumos(id),
            tipo TEXT NOT NULL CHECK(tipo IN ('Entrada','Salida')),
            cantidad REAL NOT NULL CHECK(cantidad > 0),
            motivo TEXT NOT NULL DEFAULT '',
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ordenes_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER NOT NULL REFERENCES proveedores_javier(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            estado TEXT NOT NULL DEFAULT 'Pendiente'
        );
        CREATE TABLE IF NOT EXISTS detalle_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL REFERENCES ordenes_compra(id),
            insumo_id INTEGER NOT NULL REFERENCES insumos(id),
            cantidad REAL NOT NULL CHECK(cantidad > 0)
        );
        """)
        # Si Said creó `insumos` antes con menos columnas, se agregan sin borrar nada.
        columnas = [col[1] for col in c.execute("PRAGMA table_info(insumos)")]
        faltantes = {
            "unidad": "TEXT NOT NULL DEFAULT 'pieza'",
            "existencia": "REAL NOT NULL DEFAULT 0",
            "minimo": "REAL NOT NULL DEFAULT 0",
            "activo": "INTEGER NOT NULL DEFAULT 1",
        }
        for nombre, definicion in faltantes.items():
            if nombre not in columnas:
                c.execute(f"ALTER TABLE insumos ADD COLUMN {nombre} {definicion}")


# ================================================================
# SPRINT 3 - TAREA 39
# Nombre: Registrar salidas por uso o desperdicio
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Resta la cantidad del insumo y guarda el movimiento con su
#            motivo, todo en una sola transacción. Rechaza saldos negativos.
# Depende de: tabla insumos (Said T35/T36) y movimientos_inventario (Said T38).
# ================================================================
def registrar_salida(insumo_id, cantidad, motivo):
    try:
        cantidad = _cantidad(cantidad)
    except ValueError as error:
        return False, str(error)
    if motivo not in MOTIVOS_SALIDA:
        return False, "Selecciona el motivo: Uso o Desperdicio."
    c = conectar()
    try:
        c.execute("BEGIN IMMEDIATE")  # Bloquea la escritura: evita dos salidas al mismo tiempo.
        insumo = c.execute("SELECT nombre, existencia, unidad FROM insumos WHERE id=? AND activo=1",
                           (insumo_id,)).fetchone()
        if insumo is None:
            return False, "El insumo no existe."
        nombre, existencia, unidad = insumo
        if cantidad > _redondear(existencia):
            return False, (f"No hay suficiente {nombre}. Existencia: {_formato(existencia)} {unidad}; "
                           f"intentaste retirar {_formato(cantidad)} {unidad}.")
        # La condición existencia >= ? es una segunda protección contra saldos negativos.
        cambio = c.execute("""UPDATE insumos SET existencia = ROUND(existencia - ?, 3)
                              WHERE id=? AND existencia >= ?""", (cantidad, insumo_id, cantidad))
        if cambio.rowcount != 1:
            return False, "No se pudo descontar: la existencia cambió. Actualiza e intenta de nuevo."
        c.execute("""INSERT INTO movimientos_inventario(insumo_id, tipo, cantidad, motivo)
                     VALUES (?, 'Salida', ?, ?)""", (insumo_id, cantidad, motivo))
        c.commit()
        nueva = _redondear(existencia - cantidad)
        return True, f"Salida registrada ({motivo}). {nombre}: quedan {_formato(nueva)} {unidad}."
    except sqlite3.DatabaseError as error:
        return False, f"No se pudo registrar la salida: {error}"
    finally:
        c.close()  # Sin commit, SQLite revierte los cambios.


def listar_movimientos(insumo_id=None, limite=50):
    """Historial para comprobar T39 (y entradas T38): (id, insumo, tipo, cantidad, unidad, motivo, fecha)."""
    sql = """SELECT mv.id, i.nombre, mv.tipo, mv.cantidad, i.unidad, mv.motivo,
                    datetime(mv.fecha, 'localtime')
             FROM movimientos_inventario mv JOIN insumos i ON i.id = mv.insumo_id"""
    parametros = []
    if insumo_id is not None:
        sql += " WHERE mv.insumo_id = ?"
        parametros.append(insumo_id)
    sql += " ORDER BY mv.id DESC LIMIT ?"
    parametros.append(limite)
    with conectar() as c:
        return c.execute(sql, parametros).fetchall()


# ================================================================
# SPRINT 3 - TAREA 40
# Nombre: Mostrar existencias actualizadas
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Lee las existencias directamente de SQLite (no de variables
#            temporales) para que la pantalla siempre muestre el saldo real.
# Depende de: T36 (existencia y unidad), T38 entradas, T39 salidas.
# ================================================================
def listar_existencias():
    """Cada fila: (id, nombre, existencia, unidad, minimo)."""
    with conectar() as c:
        filas = c.execute("""SELECT id, nombre, existencia, unidad, minimo FROM insumos
                             WHERE activo=1 ORDER BY nombre, id""").fetchall()
    return [(i, n, _redondear(e), u, _redondear(m)) for i, n, e, u, m in filas]


# ================================================================
# SPRINT 3 - TAREA 42
# Nombre: Mostrar ingredientes bajo mínimo
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Lista los insumos cuya existencia es MENOR que el mínimo y
#            calcula cuánto falta. Criterio: existencia igual al mínimo NO
#            es alerta (confirmarlo con Said, T37).
# Depende de: T36/T37 (existencia y mínimo), T40.
# ================================================================
def listar_bajo_minimo():
    """Cada fila: (id, nombre, existencia, minimo, unidad, faltante)."""
    with conectar() as c:
        filas = c.execute("""SELECT id, nombre, existencia, minimo, unidad FROM insumos
                             WHERE activo=1 AND ROUND(existencia, 3) < ROUND(minimo, 3)
                             ORDER BY nombre, id""").fetchall()
    return [(i, n, _redondear(e), _redondear(m), u, _redondear(m - e)) for i, n, e, m, u in filas]


# ================================================================
# SPRINT 3 - TAREA 43
# Nombre: Crear órdenes de compra
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Guarda la cabecera (folio, proveedor, fecha, estado Pendiente)
#            y su detalle (insumos y cantidades) en una sola transacción.
#            NO aumenta existencias: eso pasa al recibir la orden (Aarón T44).
# Depende de: proveedores_javier (Javier T41) e insumos (Said T35).
# ================================================================
def listar_proveedores_activos():
    """(id, nombre) de los proveedores de Javier (T41)."""
    with conectar() as c:
        return c.execute("SELECT id, nombre FROM proveedores_javier WHERE activo=1 ORDER BY nombre, id").fetchall()


def crear_orden_compra(proveedor_id, renglones):
    """renglones: lista de (insumo_id, cantidad). Devuelve (ok, mensaje, folio)."""
    if proveedor_id is None:
        return False, "Selecciona un proveedor.", None
    if not renglones:
        return False, "Agrega al menos un ingrediente a la orden.", None
    # Si el mismo insumo se agregó dos veces, se suman sus cantidades.
    cantidades = {}
    try:
        for insumo_id, cantidad in renglones:
            cantidades[insumo_id] = round(cantidades.get(insumo_id, 0) + _cantidad(cantidad), 3)
    except ValueError as error:
        return False, str(error), None
    c = conectar()
    try:
        c.execute("BEGIN IMMEDIATE")
        proveedor = c.execute("SELECT id FROM proveedores_javier WHERE id=? AND activo=1",
                              (proveedor_id,)).fetchone()
        if proveedor is None:
            return False, "El proveedor no existe.", None
        for insumo_id in cantidades:
            if c.execute("SELECT 1 FROM insumos WHERE id=? AND activo=1", (insumo_id,)).fetchone() is None:
                return False, "Uno de los ingredientes ya no existe.", None
        folio = c.execute("INSERT INTO ordenes_compra(proveedor_id, estado) VALUES (?, 'Pendiente')",
                          (proveedor_id,)).lastrowid
        c.executemany("INSERT INTO detalle_compra(orden_id, insumo_id, cantidad) VALUES (?, ?, ?)",
                      [(folio, insumo_id, cant) for insumo_id, cant in cantidades.items()])
        c.commit()
        return True, f"Orden de compra #{folio} guardada con estado Pendiente.", folio
    except sqlite3.DatabaseError as error:
        return False, f"No se pudo guardar la orden: {error}", None
    finally:
        c.close()


def listar_ordenes_compra():
    """(folio, proveedor, fecha, estado, número de renglones)."""
    with conectar() as c:
        return c.execute("""SELECT oc.id, p.nombre, datetime(oc.fecha, 'localtime'), oc.estado,
                                   (SELECT COUNT(*) FROM detalle_compra d WHERE d.orden_id = oc.id)
                            FROM ordenes_compra oc JOIN proveedores_javier p ON p.id = oc.proveedor_id
                            ORDER BY oc.id DESC""").fetchall()


def obtener_orden_compra(folio):
    """Devuelve (cabecera, renglones) o (None, []). Cabecera: (folio, proveedor, fecha, estado).
    Renglón: (insumo, cantidad, unidad)."""
    with conectar() as c:
        cabecera = c.execute("""SELECT oc.id, p.nombre, datetime(oc.fecha, 'localtime'), oc.estado
                                FROM ordenes_compra oc JOIN proveedores_javier p ON p.id = oc.proveedor_id
                                WHERE oc.id=?""", (folio,)).fetchone()
        if cabecera is None:
            return None, []
        renglones = c.execute("""SELECT i.nombre, d.cantidad, i.unidad FROM detalle_compra d
                                 JOIN insumos i ON i.id = d.insumo_id
                                 WHERE d.orden_id=? ORDER BY d.id""", (folio,)).fetchall()
    return cabecera, [(n, _redondear(cant), u) for n, cant, u in renglones]
