"""Prueba integración T25-T44 con SQLite temporal: no altera restaurante.db."""
import tempfile,os
import base_datos as bd
import javier_caja_proveedores as j
import pato_almacen as p
import sprint3_nuevo as s
with tempfile.TemporaryDirectory() as tmp:
    bd.NOMBRE_BD=os.path.join(tmp,'test.db')
    bd.inicializar_base_de_datos();j.preparar_tablas_javier();p.preparar_tablas_pato()
    assert s.registrar_insumo('Arroz','kg',3,5)[0]
    assert not s.registrar_insumo('Arroz','kg')[0]
    ins=p.listar_existencias()[0][0]
    assert p.listar_bajo_minimo()[0][1]=='Arroz'
    assert s.registrar_entrada(ins,4)[0]
    assert p.listar_existencias()[0][2]==7
    assert s.modificar_minimo(ins,8)[0]
    assert p.listar_bajo_minimo()[0][-1]==1
    assert p.registrar_salida(ins,2,'Uso')[0]
    assert p.listar_existencias()[0][2]==5
    assert j.registrar_proveedor('Proveedor A')[0]
    proveedor=j.listar_proveedores()[0][0]
    ok,_,oc=p.crear_orden_compra(proveedor,[(ins,3)])
    assert ok
    assert not s.cambiar_estado_compra(oc,'Recibida')[0]
    assert s.cambiar_estado_compra(oc,'Solicitada')[0]
    assert s.cambiar_estado_compra(oc,'Recibida')[0]
    assert not s.cambiar_estado_compra(oc,'Recibida')[0]
    assert p.listar_existencias()[0][2]==8
    assert bd.registrar_mesa(777)[0]
    assert bd.registrar_producto('Taco','Comida','',20)[0]
    mesa=next(x[0] for x in bd.listar_mesas() if x[1]==777)
    prod=next(x[0] for x in bd.listar_productos() if x[1]=='Taco')
    ok,_,pedido=bd.crear_pedido(mesa);assert ok
    assert bd.agregar_producto_pedido(pedido,prod,2,'sin cebolla')[0]
    assert bd.enviar_pedido_cocina(pedido)[0]
    assert bd.marcar_pedido_en_preparacion(pedido)[0]
    assert s.marcar_listo(pedido)[0]
    assert not s.marcar_listo(pedido)[0]
    assert (pedido,777) in s.listar_listos()
    assert s.marcar_entregado(pedido)[0]
    assert not s.marcar_entregado(pedido)[0]
    assert (pedido,777) not in s.listar_listos()
    assert s.cuentas_pendientes()[0][2]=='40.00'
    assert s.cuenta_mesa(mesa)['total']=='40.00'
    assert not s.cerrar_mesa(mesa)[0]
    ok,_,folio=j.registrar_pago(mesa,'Efectivo','50');assert ok
    assert s.cerrar_mesa(mesa)[0]
    assert not s.cerrar_mesa(mesa)[0]
    assert next(x[2] for x in bd.listar_mesas() if x[0]==mesa)=='Libre'
    with bd.conectar() as c:
        assert c.execute('SELECT estado FROM pedidos WHERE id=?',(pedido,)).fetchone()[0]=='Entregado'
        assert c.execute('SELECT COUNT(*) FROM movimientos_inventario').fetchone()[0]==3
    print('OK: Sprint 3 T25-T44, compras, inventario, pagos, cierre e historial.')
