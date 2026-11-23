# ================================================================
# RESPONSABILIDAD / MÓDULO: Javier Tadeo | Sprint 3 | cobros, tickets y proveedores
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""SPRINT 3 | Javier Tadeo: T31 (pagos), T32 (cambio), T33 (ticket), T41 (proveedores).
Módulo independiente: utiliza la conexión del equipo sin reemplazar otras funciones.
"""
import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from base_datos import conectar

CENTAVOS = Decimal('0.01')

def _dinero(valor):
    """Evita errores típicos de sumar flotantes para importes monetarios."""
    try:
        numero = Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
        if not numero.is_finite() or numero < 0:
            raise ValueError
        return numero
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError('Ingresa un importe válido, igual o mayor a cero.')


def preparar_tablas_javier():
    """T31/T33/T41: agrega tablas nuevas sin borrar ni alterar las del Sprint 1/2.
    Se ejecuta al arrancar; CREATE TABLE IF NOT EXISTS conserva registros anteriores.
    """
    with conectar() as c:
        c.execute('PRAGMA foreign_keys=ON')
        c.executescript('''
        CREATE TABLE IF NOT EXISTS pagos_javier (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          mesa_id INTEGER NOT NULL REFERENCES mesas(id),
          metodo TEXT NOT NULL CHECK(metodo IN ('Efectivo','Tarjeta')),
          total TEXT NOT NULL,
          recibido TEXT NOT NULL,
          cambio TEXT NOT NULL,
          fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pago_pedidos_javier (
          pago_id INTEGER NOT NULL REFERENCES pagos_javier(id),
          pedido_id INTEGER NOT NULL UNIQUE REFERENCES pedidos(id),
          PRIMARY KEY (pago_id,pedido_id)
        );
        CREATE TABLE IF NOT EXISTS pago_lineas_javier (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          pago_id INTEGER NOT NULL REFERENCES pagos_javier(id),
          producto TEXT NOT NULL,
          cantidad INTEGER NOT NULL,
          precio_unitario TEXT NOT NULL,
          importe TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proveedores_javier (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nombre TEXT NOT NULL,
          telefono TEXT NOT NULL DEFAULT '',
          correo TEXT NOT NULL DEFAULT '',
          activo INTEGER NOT NULL DEFAULT 1
        );
        ''')


def _detalle_por_mesa(c, mesa_id):
    """T31: recoge únicamente pedidos Entregados todavía no cobrados.
    T27, implementada por Aarón, será quien genere ese estado.
    """
    pedidos = c.execute('''SELECT pe.id FROM pedidos pe
      WHERE pe.mesa_id=? AND pe.estado='Entregado'
        AND NOT EXISTS(SELECT 1 FROM pago_pedidos_javier pp WHERE pp.pedido_id=pe.id)
      ORDER BY pe.id''',(mesa_id,)).fetchall()
    ids = [x[0] for x in pedidos]
    detalles = []
    for pid in ids:
        detalles.extend(c.execute('''SELECT pr.nombre,dp.cantidad,pr.precio
           FROM detalle_pedido dp JOIN productos pr ON pr.id=dp.producto_id
           WHERE dp.pedido_id=? ORDER BY dp.id''',(pid,)).fetchall())
    return ids, detalles


def listar_cuentas_por_cobrar():
    """Interfaz auxiliar T31: muestra mesas con pedidos entregados sin cobrar.
    Es una consulta propia; no modifica la tarea T30 de Juan.
    """
    with conectar() as c:
        filas = c.execute('''SELECT DISTINCT m.id,m.numero FROM mesas m JOIN pedidos pe
           ON pe.mesa_id=m.id WHERE pe.estado='Entregado'
           AND NOT EXISTS(SELECT 1 FROM pago_pedidos_javier x WHERE x.pedido_id=pe.id)
           ORDER BY m.numero''').fetchall()
        resultado=[]
        for mid, numero in filas:
            _, detalles=_detalle_por_mesa(c,mid)
            total=sum((_dinero(precio)*cant for _,cant,precio in detalles),Decimal('0.00'))
            resultado.append((mid,numero,f'{total:.2f}'))
        return resultado


def consultar_cuenta(mesa_id):
    """Datos del consumo sin cobrar para mostrar el desglose antes del pago."""
    with conectar() as c:
        pedidos, detalles = _detalle_por_mesa(c,mesa_id)
    lineas = []
    for nombre,cantidad,precio in detalles:
        precio=_dinero(precio)
        importe=(precio*cantidad).quantize(CENTAVOS)
        lineas.append({'producto':nombre,'cantidad':cantidad,'precio':f'{precio:.2f}', 'importe':f'{importe:.2f}'})
    total=sum((Decimal(x['importe']) for x in lineas),Decimal('0.00'))
    return {'pedidos':pedidos,'lineas':lineas,'total':f'{total:.2f}'}


def calcular_cambio(total, recibido):
    """T32: calcula la diferencia; rechaza pagos en efectivo insuficientes."""
    try:
        total, recibido = _dinero(total), _dinero(recibido)
    except ValueError as e:
        return False,str(e),None
    if recibido < total:
        return False,'El efectivo recibido no alcanza para pagar la cuenta.',None
    return True,'Cambio calculado.',f'{recibido-total:.2f}'


def registrar_pago(mesa_id, metodo, recibido=None):
    """T31/T32: confirma un pago una sola vez usando una transacción SQLite.
    Las líneas del ticket se copian al momento de cobrar y no cambian si
    después se modifica el nombre o precio de un producto del catálogo.
    Retorna (correcto, mensaje, folio_pago).
    """
    if metodo not in ('Efectivo','Tarjeta'):
        return False,'Selecciona Efectivo o Tarjeta.',None
    c=conectar()
    try:
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('BEGIN IMMEDIATE')  # Impide dos cobros simultáneos del mismo pedido.
        mesa=c.execute('SELECT numero FROM mesas WHERE id=?',(mesa_id,)).fetchone()
        if not mesa:
            return False,'La mesa no existe.',None
        pedidos,detalles=_detalle_por_mesa(c,mesa_id)
        if not pedidos or not detalles:
            return False,'No hay pedidos entregados pendientes de cobro.',None
        lineas=[]
        total=Decimal('0.00')
        for nombre,cantidad,precio in detalles:
            precio=_dinero(precio)
            subtotal=(precio*cantidad).quantize(CENTAVOS)
            total+=subtotal
            lineas.append((nombre,cantidad,f'{precio:.2f}',f'{subtotal:.2f}'))
        if metodo=='Efectivo':
            ok,mensaje,cambio=calcular_cambio(total,recibido)
            if not ok:
                return False,mensaje,None
            recibido=_dinero(recibido)
        else:
            recibido=total
            cambio='0.00'
        cur=c.execute('''INSERT INTO pagos_javier(mesa_id,metodo,total,recibido,cambio)
                         VALUES (?,?,?,?,?)''',(mesa_id,metodo,f'{total:.2f}',f'{recibido:.2f}',cambio))
        pago_id=cur.lastrowid
        c.executemany('INSERT INTO pago_pedidos_javier(pago_id,pedido_id) VALUES (?,?)',[(pago_id,pid) for pid in pedidos])
        c.executemany('''INSERT INTO pago_lineas_javier(pago_id,producto,cantidad,precio_unitario,importe)
                         VALUES (?,?,?,?,?)''',[(pago_id,*l) for l in lineas])
        c.commit()
        return True,'Pago registrado correctamente.',pago_id
    except (sqlite3.DatabaseError,ValueError) as e:
        return False,f'No se pudo registrar el pago: {e}',None
    finally:
        c.close()  # Si no hubo commit, se revierte la transacción.


def obtener_ticket(pago_id):
    """T33: recupera el comprobante histórico para consultar o guardar."""
    with conectar() as c:
        cabecera=c.execute('''SELECT p.id,m.numero,p.metodo,p.total,p.recibido,p.cambio,p.fecha
            FROM pagos_javier p JOIN mesas m ON m.id=p.mesa_id WHERE p.id=?''',(pago_id,)).fetchone()
        if not cabecera:
            return None
        productos=c.execute('''SELECT producto,cantidad,precio_unitario,importe
            FROM pago_lineas_javier WHERE pago_id=? ORDER BY id''',(pago_id,)).fetchall()
    return cabecera,productos


def generar_texto_ticket(pago_id):
    """T33: arma un ticket de texto; no necesita impresora ni librerías extras."""
    ticket=obtener_ticket(pago_id)
    if not ticket:
        return None
    (folio,mesa,metodo,total,recibido,cambio,fecha),productos=ticket
    texto=['SISTEMA DE COMANDAS - TICKET',f'Folio de pago: {folio}',f'Fecha: {fecha}',f'Mesa: {mesa}','-'*42]
    for nombre,cant,precio,importe in productos:
        texto.append(f'{cant} x {nombre} (${precio}) = ${importe}')
    texto.extend(['-'*42,f'Total: ${total}',f'Método: {metodo}',f'Recibido: ${recibido}',f'Cambio: ${cambio}','Gracias por su visita'])
    return '\n'.join(texto)+'\n'


def registrar_proveedor(nombre,telefono='',correo=''):
    """T41: guarda un proveedor para futuras órdenes de compra T43 de Pato."""
    nombre,telefono,correo=(nombre or '').strip(),(telefono or '').strip(),(correo or '').strip()
    if not nombre:
        return False,'Escribe el nombre del proveedor.'
    if correo and ('@' not in correo or '.' not in correo.split('@')[-1]):
        return False,'Escribe un correo válido o déjalo vacío.'
    if len(nombre)>120 or len(telefono)>40 or len(correo)>150:
        return False,'Algún dato es demasiado largo.'
    with conectar() as c:
        c.execute('INSERT INTO proveedores_javier(nombre,telefono,correo) VALUES (?,?,?)',(nombre,telefono,correo))
    return True,'Proveedor registrado correctamente.'


def listar_proveedores():
    """T41: lista los proveedores activos ordenados por nombre."""
    with conectar() as c:
        return c.execute('SELECT id,nombre,telefono,correo FROM proveedores_javier WHERE activo=1 ORDER BY nombre,id').fetchall()
