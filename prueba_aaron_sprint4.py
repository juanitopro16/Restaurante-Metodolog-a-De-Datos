# Prueba de Aarón - Sprint 4 (T48, T59, T60, T61).
# Usa una base de datos TEMPORAL: no toca restaurante.db.
# Ejecutar desde la carpeta del proyecto:   py prueba_aaron_sprint4.py
import os
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import base_datos
carpeta = tempfile.mkdtemp()
base_datos.NOMBRE_BD = os.path.join(carpeta, "prueba_aaron.db")
base_datos.inicializar_base_de_datos()

from javier_caja_proveedores import preparar_tablas_javier, registrar_pago
from sprint3_nuevo import marcar_listo, marcar_entregado, cerrar_mesa
import aaron_sprint4 as a

preparar_tablas_javier()
fallas = []


def comprobar(nombre, condicion, detalle=""):
    print(("OK    " if condicion else "FALLA ") + nombre + (f"  -> {detalle}" if detalle and not condicion else ""))
    if not condicion:
        fallas.append(nombre)


# ---------- Datos de prueba ----------
base_datos.registrar_mesa(1)
base_datos.registrar_mesa(2)
mesas = {m[1]: m[0] for m in base_datos.listar_mesas()}
base_datos.registrar_producto("Taco", "Platillo", "", 35)
base_datos.registrar_producto("Agua", "Bebida", "", 20)
prod = {p[1]: p[0] for p in base_datos.listar_productos()}

# ---------- T61: migración ----------
a.asegurar_columna_envio()
a.asegurar_columna_envio()   # repetirla no debe fallar
c = base_datos.conectar()
columnas = [f[1] for f in c.execute("PRAGMA table_info(pedidos)")]
c.close()
comprobar("T61 migración: existe pedidos.fecha_hora_envio (y es repetible)",
          "fecha_hora_envio" in columnas)

# ---------- T59: crear y editar borrador ----------
ok, _, pid = base_datos.crear_pedido(mesas[1])
comprobar("T59 crear pedido en mesa libre", ok)
ok1, _ = base_datos.agregar_producto_pedido(pid, prod["Taco"], 2, "sin cebolla")
ok2, _ = base_datos.agregar_producto_pedido(pid, prod["Agua"], 1, "")
comprobar("T59 agregar dos productos", ok1 and ok2)
detalle = base_datos.listar_detalle_pedido(pid)
ok, _ = base_datos.modificar_detalle_pedido(detalle[0][0], 3, "sin cebolla")
comprobar("T59 modificar cantidad en borrador", ok)
ok, _ = base_datos.quitar_producto_pedido(detalle[1][0])
comprobar("T59 quitar un producto en borrador", ok)
vacio_ok, _, pid_vacio = base_datos.crear_pedido(mesas[2])
ok, msg = a.enviar_pedido_cocina_t61(pid_vacio)
comprobar("T59/T61 no deja enviar un pedido vacío", not ok, msg)

# ---------- T61: envío con hora ----------
ok, msg = a.enviar_pedido_cocina_t61(pid)
comprobar("T61 enviar a cocina guarda estado Pendiente", ok, msg)
c = base_datos.conectar()
estado, envio = c.execute("SELECT estado, fecha_hora_envio FROM pedidos WHERE id=?", (pid,)).fetchone()
c.close()
comprobar("T61 se guardó la hora de envío", estado == "Pendiente" and bool(envio), (estado, envio))
ok, _ = a.enviar_pedido_cocina_t61(pid)
comprobar("T21/T61 no se puede enviar dos veces", not ok)
ok, _ = base_datos.modificar_detalle_pedido(detalle[0][0], 9, "")
comprobar("T59 pedido enviado ya no se puede modificar", not ok)
ok, _ = base_datos.quitar_producto_pedido(detalle[0][0])
comprobar("T59 pedido enviado ya no se puede quitar producto", not ok)

# ---------- T61: cálculo de minutos ----------
base = datetime(2026, 11, 20, 10, 0, 0)
comprobar("T61 minutos: 7 min 30 s -> 7",
          a.minutos_transcurridos("2026-11-20 10:00:00", base + timedelta(minutes=7, seconds=30)) == 7)
comprobar("T61 minutos: hora en el futuro -> 0",
          a.minutos_transcurridos("2026-11-20 10:00:00", base - timedelta(minutes=3)) == 0)
comprobar("T61 minutos: sin dato -> None", a.minutos_transcurridos(None) is None)
comprobar("T61 minutos: dato inválido -> None", a.minutos_transcurridos("basura") is None)

# ---------- T60: datos de las tarjetas ----------
cmds = a.listar_comandas_cocina(ahora=datetime.now() + timedelta(minutes=12))
comprobar("T60 aparece 1 comanda Pendiente", len(cmds) == 1 and cmds[0]["estado"] == "Pendiente", cmds)
comprobar("T60 trae mesa, productos, cantidad y nota",
          cmds[0]["mesa"] == 1 and cmds[0]["productos"] == [(3, "Taco", "sin cebolla")], cmds[0]["productos"])
comprobar("T61 la espera visible es de ~12 min", cmds[0]["minutos"] in (11, 12, 13), cmds[0]["minutos"])
ok, _ = base_datos.marcar_pedido_en_preparacion(pid)
cmds = a.listar_comandas_cocina()
comprobar("T60 pasa a En preparación", ok and cmds[0]["estado"] == "En preparación")
ok, _ = marcar_listo(pid)
cmds = a.listar_comandas_cocina()
comprobar("T60 pasa a Listo", ok and cmds[0]["estado"] == "Listo")
ok, _ = marcar_listo(pid)
comprobar("T60 no se puede marcar Listo dos veces", not ok)
ok, _ = marcar_entregado(pid)
comprobar("T60 entregado sale de cocina", ok and a.listar_comandas_cocina() == [])

# ---------- Pedido antiguo sin hora (anterior a la migración) ----------
c = base_datos.conectar()
c.execute("INSERT INTO pedidos(mesa_id,estado) VALUES(?, 'Pendiente')", (mesas[2],))
c.commit()
c.close()
antiguo = [x for x in a.listar_comandas_cocina() if x["estado"] == "Pendiente"]
comprobar("T61 pedido antiguo sin hora muestra minutos=None (se verá '—')",
          len(antiguo) == 1 and antiguo[0]["minutos"] is None)
c = base_datos.conectar()
c.execute("DELETE FROM pedidos WHERE estado='Pendiente' AND fecha_hora_envio IS NULL")
c.execute("UPDATE mesas SET estado='Libre' WHERE id=?", (mesas[2],))
c.commit()
c.close()

# ---------- T48: cobrar, cerrar mesa e historial ----------
ok, msg, folio_pago = registrar_pago(mesas[1], "Efectivo", "200")
comprobar("T48 cobrar en efectivo", ok, msg)
ok, msg = cerrar_mesa(mesas[1])
comprobar("T48 cerrar mesa", ok, msg)
hist = a.listar_historial_pedidos()
comprobar("T48 el historial muestra el pedido cobrado (1 registro)", len(hist) == 1, hist)
h = hist[0]
comprobar("T48 historial: folio, mesa, método y total",
          h["folio"] == pid and h["mesa"] == 1 and h["metodo"] == "Efectivo"
          and float(h["total_pago"]) == 105.0, h)
ok, _ = cerrar_mesa(mesas[1])
comprobar("T48 cerrar la mesa otra vez es rechazado", not ok)
comprobar("T48 no se duplica el historial", len(a.listar_historial_pedidos()) == 1)
det = a.obtener_historial_pedido(pid)
comprobar("T48 detalle: productos del pedido", det is not None and det["productos_pedido"] == [(3, "Taco", "sin cebolla")])
comprobar("T48 detalle: líneas del pago congeladas",
          det["lineas_pago"] == [("Taco", 3, "35.00", "105.00")], det["lineas_pago"])
comprobar("T48 detalle: pago en efectivo con cambio",
          det["pago"]["metodo"] == "Efectivo" and float(det["pago"]["cambio"]) == 95.0, det["pago"])

# El precio histórico no cambia si se edita el catálogo
base_datos.modificar_producto(prod["Taco"], "Taco", "", 99)
det2 = a.obtener_historial_pedido(pid)
comprobar("T48 el precio histórico no cambia al editar el catálogo",
          det2["lineas_pago"] == det["lineas_pago"])
comprobar("T48 pedido sin pago devuelve None", a.obtener_historial_pedido(99999) is None)

print()
if fallas:
    print(f"{len(fallas)} prueba(s) fallaron:")
    for f in fallas:
        print(" -", f)
    sys.exit(1)
print("Todas las pruebas de Aarón pasaron.")
