# ================================================================
# RESPONSABILIDAD / MÓDULO: Equipo Sprint 3 | Sprint 3 | pedidos, entrega, insumos y compras
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Sprint 3: funciones pendientes de Aarón (T25-27,44), Said (T35-38), Juan (T28-30,34).
Mantiene las tablas existentes de Javier y Pato. Proyecto académico de demostración.
"""
from decimal import Decimal, InvalidOperation
import sqlite3
from base_datos import conectar


def _positivo(valor):
    try:
        d=Decimal(str(valor).replace(',','.'))
        if not d.is_finite() or d<=0 or d.as_tuple().exponent < -3: raise ValueError
        return float(d)
    except (ValueError, InvalidOperation, TypeError):
        raise ValueError('Escribe una cantidad positiva con máximo 3 decimales.')

# Said: T35 catálogo, T36 unidades/existencias, T37 mínimos, T38 entradas.
def registrar_insumo(nombre, unidad, existencia=0, minimo=0):
    nombre=nombre.strip(); unidad=unidad.strip()
    if not nombre or not unidad: return False,'Nombre y unidad son obligatorios.'
    try:
        e=float(str(existencia).replace(',','.')); m=float(str(minimo).replace(',','.'))
        if not (0<=e<1e9 and 0<=m<1e9): raise ValueError
    except ValueError: return False,'Existencia y mínimo deben ser números no negativos.'
    with conectar() as c:
        if c.execute('SELECT 1 FROM insumos WHERE lower(nombre)=lower(?) AND activo=1',(nombre,)).fetchone():
            return False,'Ya existe un insumo con ese nombre.'
        c.execute('INSERT INTO insumos(nombre,unidad,existencia,minimo) VALUES(?,?,?,?)',(nombre,unidad,round(e,3),round(m,3)))
    return True,'Insumo registrado.'

def modificar_minimo(insumo_id, minimo):
    try:
        m=float(str(minimo).replace(',','.'))
        if not 0<=m<1e9: raise ValueError
    except ValueError: return False,'Mínimo inválido.'
    with conectar() as c:
        cur=c.execute('UPDATE insumos SET minimo=? WHERE id=? AND activo=1',(round(m,3),insumo_id))
        return (cur.rowcount==1,'Mínimo actualizado.' if cur.rowcount else 'Insumo no encontrado.')

def registrar_entrada(insumo_id, cantidad, motivo='Compra'):
    try: cantidad=_positivo(cantidad)
    except ValueError as e: return False,str(e)
    c=conectar()
    try:
        c.execute('BEGIN IMMEDIATE')
        cur=c.execute('UPDATE insumos SET existencia=ROUND(existencia+?,3) WHERE id=? AND activo=1',(cantidad,insumo_id))
        if cur.rowcount!=1: return False,'Insumo inexistente.'
        c.execute("INSERT INTO movimientos_inventario(insumo_id,tipo,cantidad,motivo) VALUES(?,'Entrada',?,?)",(insumo_id,cantidad,motivo))
        c.commit(); return True,'Entrada registrada y existencias actualizadas.'
    except sqlite3.DatabaseError as e: return False,str(e)
    finally: c.close()

# Aarón: T25 marcar Listo, T26 avisar a mesero mediante consulta, T27 entregar.
def marcar_listo(pedido_id):
    with conectar() as c:
        cur=c.execute("UPDATE pedidos SET estado='Listo' WHERE id=? AND estado='En preparación'",(pedido_id,))
        return (cur.rowcount==1,'Pedido listo para entregar.' if cur.rowcount else 'El pedido no está En preparación.')

def listar_listos():
    with conectar() as c:
        return c.execute("SELECT p.id,m.numero FROM pedidos p JOIN mesas m ON m.id=p.mesa_id WHERE p.estado='Listo' ORDER BY p.id").fetchall()

def marcar_entregado(pedido_id):
    with conectar() as c:
        cur=c.execute("UPDATE pedidos SET estado='Entregado' WHERE id=? AND estado='Listo'",(pedido_id,))
        return (cur.rowcount==1,'Pedido entregado a la mesa.' if cur.rowcount else 'Solo pueden entregarse pedidos Listos.')

# Juan: T28 detalle por mesa, T29 subtotales, T30 pendientes, T34 cerrar mesa.
def cuenta_mesa(mesa_id):
    from javier_caja_proveedores import consultar_cuenta
    return consultar_cuenta(mesa_id)

def cuentas_pendientes():
    from javier_caja_proveedores import listar_cuentas_por_cobrar
    return listar_cuentas_por_cobrar()

def cerrar_mesa(mesa_id):
    """Solo libera si hubo pago y no hay pedidos sin cobrar o en proceso.
    No borra pedidos ni pagos históricos. Bloquea cierre repetido.
    """
    c=conectar()
    try:
        c.execute('BEGIN IMMEDIATE')
        mesa=c.execute('SELECT estado FROM mesas WHERE id=?',(mesa_id,)).fetchone()
        if not mesa or mesa[0]!='Ocupada': return False,'La mesa no está ocupada.'
        pago=c.execute('SELECT 1 FROM pagos_javier WHERE mesa_id=? LIMIT 1',(mesa_id,)).fetchone()
        if not pago: return False,'Registra primero el pago.'
        sin_pagar=c.execute("""SELECT COUNT(*) FROM pedidos p WHERE p.mesa_id=?
          AND (p.estado!='Entregado' OR NOT EXISTS
          (SELECT 1 FROM pago_pedidos_javier pp WHERE pp.pedido_id=p.id))""",(mesa_id,)).fetchone()[0]
        if sin_pagar: return False,'Hay pedidos en proceso o entregados sin cobrar.'
        c.execute("UPDATE mesas SET estado='Libre' WHERE id=?",(mesa_id,))
        c.commit(); return True,'Cuenta cerrada. Mesa libre; historial conservado.'
    finally: c.close()

# Aarón: T44 estados de órdenes, recepción con entrada de inventario atómica.
def cambiar_estado_compra(orden_id, nuevo_estado):
    if nuevo_estado not in ('Solicitada','Recibida'):
        return False,'Estado inválido.'
    c=conectar()
    try:
        c.execute('BEGIN IMMEDIATE')
        fila=c.execute('SELECT estado FROM ordenes_compra WHERE id=?',(orden_id,)).fetchone()
        if not fila: return False,'Orden no encontrada.'
        actual=fila[0]
        if nuevo_estado=='Solicitada' and actual!='Pendiente': return False,'Solo una orden Pendiente puede solicitarse.'
        if nuevo_estado=='Recibida' and actual!='Solicitada': return False,'Primero debe solicitarse; no se permite recibir dos veces.'
        if nuevo_estado=='Recibida':
            detalles=c.execute('SELECT insumo_id,cantidad FROM detalle_compra WHERE orden_id=?',(orden_id,)).fetchall()
            if not detalles: return False,'Orden sin ingredientes.'
            for insumo_id,cantidad in detalles:
                cur=c.execute('UPDATE insumos SET existencia=ROUND(existencia+?,3) WHERE id=? AND activo=1',(cantidad,insumo_id))
                if cur.rowcount!=1: return False,'Un insumo ya no está disponible.'
                c.execute("INSERT INTO movimientos_inventario(insumo_id,tipo,cantidad,motivo) VALUES(?,'Entrada',?,'Orden de compra #' || ?)",(insumo_id,cantidad,orden_id))
        c.execute('UPDATE ordenes_compra SET estado=? WHERE id=?',(nuevo_estado,orden_id))
        c.commit(); return True,'Orden actualizada a '+nuevo_estado+'.'
    except sqlite3.DatabaseError as e: return False,str(e)
    finally: c.close()
