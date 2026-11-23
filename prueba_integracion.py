"""Prueba T18–T24 sobre SQLite temporal, sin modificar restaurante.db."""
import tempfile
from pathlib import Path
import base_datos as bd

with tempfile.TemporaryDirectory() as tmp:
    bd.NOMBRE_BD = str(Path(tmp) / "prueba.db")
    bd.inicializar_base_de_datos()
    assert bd.registrar_mesa(999)[0]
    assert bd.registrar_producto("Producto prueba", "Platillo", "", 20)[0]
    mesa = next(m[0] for m in bd.listar_mesas() if m[1] == 999)
    producto = next(p[0] for p in bd.listar_productos() if p[1] == "Producto prueba")
    ok, _, folio = bd.crear_pedido(mesa)
    assert ok
    assert bd.agregar_producto_pedido(folio, producto, 2, "sin cebolla")[0]
    assert bd.listar_detalle_pedido(folio)[0][4] == "sin cebolla"
    assert bd.enviar_pedido_cocina(folio)[0]
    assert (folio, 999) in bd.listar_pedidos_pendientes()
    assert bd.marcar_pedido_en_preparacion(folio)[0]
    assert (folio, 999) not in bd.listar_pedidos_pendientes()
    assert not bd.marcar_pedido_en_preparacion(folio)[0]
    with bd.conectar() as conexion:
        assert conexion.execute("SELECT estado FROM pedidos WHERE id=?", (folio,)).fetchone()[0] == "En preparación"
        assert conexion.execute("SELECT COUNT(*) FROM detalle_pedido WHERE pedido_id=?", (folio,)).fetchone()[0] == 1
print("OK: flujo T18–T24, notas, persistencia y bloqueo de doble preparación")
