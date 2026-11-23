"""Pruebas de las tareas de Pato (T39, T40, T42, T43).
Usa una base TEMPORAL: no modifica restaurante.db real.
Ejecutar:  python prueba_pato_t39_t40_t42_t43.py
"""
import os
import tempfile
import base_datos as bd
import javier_caja_proveedores as j
import pato_almacen as p


def insumo(nombre, unidad, existencia, minimo):
    # Simula el alta de insumo de Said (T35/T36/T37), solo en la base temporal.
    with bd.conectar() as c:
        return c.execute("INSERT INTO insumos(nombre,unidad,existencia,minimo) VALUES (?,?,?,?)",
                         (nombre, unidad, existencia, minimo)).lastrowid


def entrada(insumo_id, cantidad):
    # Simula la entrada de Said (T38), solo en la base temporal.
    with bd.conectar() as c:
        c.execute("UPDATE insumos SET existencia = existencia + ? WHERE id=?", (cantidad, insumo_id))
        c.execute("INSERT INTO movimientos_inventario(insumo_id,tipo,cantidad,motivo) VALUES (?, 'Entrada', ?, 'Compra')",
                  (insumo_id, cantidad))


def existencia(insumo_id):
    return next(e for i, _, e, _, _ in p.listar_existencias() if i == insumo_id)


with tempfile.TemporaryDirectory() as carpeta:
    bd.NOMBRE_BD = os.path.join(carpeta, "restaurante_pruebas.db")
    bd.inicializar_base_de_datos()
    j.preparar_tablas_javier()
    p.preparar_tablas_pato()
    p.preparar_tablas_pato()  # Se puede llamar dos veces sin error ni duplicar nada.

    aceite = insumo("Aceite", "L", 8, 3)
    arroz = insumo("Arroz", "kg", 3, 5)
    harina = insumo("Harina", "kg", 5, 5)

    # ---------- T39 ----------
    ok, msg = p.registrar_salida(aceite, "2", "Uso")
    assert ok, msg
    assert existencia(aceite) == 6, "Prueba 1 T39: 8 L - 2 L = 6 L"
    ok, msg = p.registrar_salida(aceite, "20", "Desperdicio")
    assert not ok and existencia(aceite) == 6, "Prueba 2 T39: no permitir saldo negativo"
    assert not p.registrar_salida(aceite, "0", "Uso")[0], "Cantidad cero rechazada"
    assert not p.registrar_salida(aceite, "-1", "Uso")[0], "Cantidad negativa rechazada"
    assert not p.registrar_salida(aceite, "abc", "Uso")[0], "Texto rechazado"
    assert not p.registrar_salida(aceite, "1", "Robo")[0], "Motivo inválido rechazado"
    assert not p.registrar_salida(9999, "1", "Uso")[0], "Insumo inexistente rechazado"
    assert p.registrar_salida(aceite, "0.5", "Desperdicio")[0]
    assert existencia(aceite) == 5.5
    motivos = [m[5] for m in p.listar_movimientos(aceite)]
    assert motivos == ["Desperdicio", "Uso"], f"Prueba 3 T39: historial con motivo {motivos}"
    print("T39 OK: 8-2=6, rechaza 20 L, historial guarda Uso/Desperdicio")

    # ---------- T40 ----------
    entrada(arroz, 1)
    assert existencia(arroz) == 4, "Prueba 1 T40: la entrada se ve inmediatamente"
    assert p.registrar_salida(arroz, "1", "Uso")[0]
    assert existencia(arroz) == 3, "Prueba 2 T40: la salida se ve inmediatamente"
    # Prueba 3 T40: abrir otra conexión (como reiniciar) y leer lo mismo.
    import sqlite3
    c = sqlite3.connect(bd.NOMBRE_BD)
    assert c.execute("SELECT existencia FROM insumos WHERE id=?", (aceite,)).fetchone()[0] == 5.5
    c.close()
    print("T40 OK: entradas y salidas se reflejan al momento y persisten en SQLite")

    # ---------- T42 ----------
    bajos = {b[1]: b for b in p.listar_bajo_minimo()}
    assert "Arroz" in bajos and bajos["Arroz"][5] == 2, "Prueba 1 T42: arroz 3 kg, mínimo 5 kg, faltan 2 kg"
    assert "Harina" not in bajos, "Prueba 3 T42: existencia igual al mínimo NO es alerta"
    assert "Aceite" not in bajos
    entrada(arroz, 4)
    assert "Arroz" not in {b[1] for b in p.listar_bajo_minimo()}, "Prueba 2 T42: con 7 kg sale de la alerta"
    print("T42 OK: muestra faltante 2 kg, desaparece al entrar 4 kg, igual al mínimo no alerta")

    # ---------- T43 ----------
    assert j.registrar_proveedor("Abarrotes Norte", "8123456789", "compras@ejemplo.com")[0]
    proveedor = j.listar_proveedores()[0][0]
    antes = (existencia(arroz), existencia(aceite))
    ok, msg, folio = p.crear_orden_compra(proveedor, [(arroz, "10"), (aceite, "4")])
    assert ok, msg
    cabecera, detalle = p.obtener_orden_compra(folio)
    assert cabecera[1] == "Abarrotes Norte" and cabecera[3] == "Pendiente"
    assert detalle == [("Arroz", 10, "kg"), ("Aceite", 4, "L")], f"Prueba 2 T43: {detalle}"
    assert (existencia(arroz), existencia(aceite)) == antes, "Crear la orden NO debe sumar existencias"
    assert not p.crear_orden_compra(None, [(arroz, "1")])[0], "Prueba 3 T43: sin proveedor"
    assert not p.crear_orden_compra(proveedor, [])[0], "Prueba 3 T43: sin ingredientes"
    assert not p.crear_orden_compra(proveedor, [(arroz, "0")])[0], "Cantidad cero rechazada"
    assert not p.crear_orden_compra(9999, [(arroz, "1")])[0], "Proveedor inexistente rechazado"
    with bd.conectar() as c:
        assert c.execute("SELECT COUNT(*) FROM ordenes_compra").fetchone()[0] == 1, "Las rechazadas no se guardan"
    ok, _, folio2 = p.crear_orden_compra(proveedor, [(arroz, "1"), (arroz, "2")])
    assert ok and p.obtener_orden_compra(folio2)[1] == [("Arroz", 3, "kg")], "Mismo insumo repetido se suma"
    print("T43 OK: orden con 2 ingredientes, se reabre el folio, rechaza sin proveedor / sin ingredientes")

print("\nTODAS LAS PRUEBAS DE PATO PASARON.")
