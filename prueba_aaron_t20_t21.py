# ================================================================
# PRUEBA AUTOMÁTICA - TAREAS 20 Y 21 (Aarón Mendoza Rodríguez)
# Trabaja sobre una COPIA temporal de restaurante.db: no modifica tu base real.
# Uso: ponlo en la misma carpeta que main.py y corre:  python prueba_aaron_t20_t21.py
# ================================================================
import os, shutil, sqlite3, tempfile
import base_datos as bd

carpeta = os.path.dirname(os.path.abspath(__file__))
original = os.path.join(carpeta, "restaurante.db")
tmp = os.path.join(tempfile.mkdtemp(), "copia.db")
if os.path.exists(original): shutil.copy(original, tmp)
bd.NOMBRE_BD = tmp
bd.inicializar_base_de_datos()

resultados = []
def revisar(nombre, condicion):
    resultados.append(condicion)
    print(("[OK]    " if condicion else "[FALLA] ") + nombre)

def consulta_directa(sql, params=()):
    # Conexión NUEVA e independiente: comprueba que el dato quedó guardado en SQLite.
    c = sqlite3.connect(tmp); filas = c.execute(sql, params).fetchall(); c.close(); return filas

# Preparación: productos y mesa de prueba (solo en la copia)
bd.registrar_producto("Prueba Tacos", "Platillo", "", 70)
bd.registrar_producto("Prueba Refresco", "Bebida", "", 25)
bd.registrar_mesa(901)
mesa = [m for m in bd.listar_mesas() if m[1] == 901][0][0]
prods = {p[1]: p[0] for p in bd.listar_productos()}
tacos, refresco = prods["Prueba Tacos"], prods["Prueba Refresco"]

print("\n--- TAREA 20 ---")
ok, _, pedido = bd.crear_pedido(mesa)
revisar("Crear pedido en Borrador", ok)
revisar("Columna notas existe en detalle_pedido",
        "notas" in [r[1] for r in consulta_directa("PRAGMA table_info(detalle_pedido)")])
bd.agregar_producto_pedido(pedido, tacos, 1, "sin cebolla")
bd.agregar_producto_pedido(pedido, refresco, 2)
det = bd.listar_detalle_pedido(pedido)
revisar("El pedido muestra 2 productos con su nota", len(det) == 2 and det[0][4] == "sin cebolla")
ok, _ = bd.modificar_detalle_pedido(det[0][0], 3, "con salsa verde")
revisar("Modificar cantidad (1 a 3) y nota", ok)
fila = consulta_directa("SELECT cantidad, notas FROM detalle_pedido WHERE id=?", (det[0][0],))[0]
revisar("PERSISTENCIA: el cambio quedó guardado en restaurante.db", fila == (3, "con salsa verde"))
ok, _ = bd.modificar_detalle_pedido(det[0][0], 0, "")
revisar("Rechaza cantidad 0", not ok)
ok, _ = bd.quitar_producto_pedido(det[1][0])
revisar("Quitar un producto", ok)
revisar("PERSISTENCIA: el producto quitado ya no está en la BD",
        len(consulta_directa("SELECT id FROM detalle_pedido WHERE pedido_id=?", (pedido,))) == 1)
revisar("Reabrir pedido desde la mesa encuentra el mismo Borrador",
        bd.obtener_pedido_borrador_mesa(mesa) == pedido)
revisar("Al reabrir, la lista conserva los cambios",
        [(d[1], d[2], d[4]) for d in bd.listar_detalle_pedido(pedido)] == [("Prueba Tacos", 3, "con salsa verde")])

print("\n--- TAREA 21 ---")
ok, _, vacio_mesa = (lambda r: r)((bd.registrar_mesa(902), None, None))
mesa2 = [m for m in bd.listar_mesas() if m[1] == 902][0][0]
_, _, pedido_vacio = bd.crear_pedido(mesa2)
ok, _ = bd.enviar_pedido_cocina(pedido_vacio)
revisar("Pedido vacío NO se puede enviar", not ok)
ok, msg = bd.enviar_pedido_cocina(pedido)
revisar("Enviar pedido con productos a cocina", ok)
revisar("PERSISTENCIA: estado cambió de Borrador a Pendiente",
        consulta_directa("SELECT estado FROM pedidos WHERE id=?", (pedido,))[0][0] == "Pendiente")
revisar("No se creó un pedido duplicado",
        consulta_directa("SELECT COUNT(*) FROM pedidos WHERE mesa_id=?", (mesa,))[0][0] == 1)
ok, _ = bd.enviar_pedido_cocina(pedido)
revisar("No se puede enviar dos veces", not ok)
revisar("Bloquea modificar después de enviar", not bd.modificar_detalle_pedido(det[0][0], 9, "x")[0])
revisar("Bloquea quitar después de enviar", not bd.quitar_producto_pedido(det[0][0])[0])
revisar("Bloquea agregar después de enviar", not bd.agregar_producto_pedido(pedido, refresco, 1)[0])

print("\n--- COCINA PUEDE CONSULTAR (lo que leerá la T22/T23 de Pato) ---")
pendientes = consulta_directa("""SELECT pe.id, m.numero, pe.estado, p.nombre, dp.cantidad, dp.notas
    FROM pedidos pe JOIN mesas m ON m.id=pe.mesa_id
    JOIN detalle_pedido dp ON dp.pedido_id=pe.id JOIN productos p ON p.id=dp.producto_id
    WHERE pe.estado='Pendiente' AND pe.id=?""", (pedido,))
print("   Lo que vería cocina:", pendientes)
revisar("Cocina ve el pedido Pendiente con mesa, producto, cantidad y nota",
        pendientes == [(pedido, 901, "Pendiente", "Prueba Tacos", 3, "con salsa verde")])

print(f"\nRESULTADO: {sum(resultados)} de {len(resultados)} pruebas correctas.")
