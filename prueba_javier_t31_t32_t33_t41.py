"""Pruebas independientes de las tareas de Javier. No modifica restaurante.db real."""
import os
import tempfile
from decimal import Decimal
import base_datos as bd
import javier_caja_proveedores as j

with tempfile.TemporaryDirectory() as carpeta:
    bd.NOMBRE_BD=os.path.join(carpeta,'restaurante_pruebas.db')
    bd.inicializar_base_de_datos()
    j.preparar_tablas_javier()
    assert bd.registrar_mesa(200)[0]
    assert bd.registrar_producto('Taco de prueba','Comida','',34.50)[0]
    mesa_id=next(x[0] for x in bd.listar_mesas() if x[1]==200)
    prod_id=next(x[0] for x in bd.listar_productos() if x[1]=='Taco de prueba')
    ok,_,pedido=bd.crear_pedido(mesa_id)
    assert ok
    assert bd.agregar_producto_pedido(pedido,prod_id,2)[0]
    assert bd.enviar_pedido_cocina(pedido)[0]
    assert bd.marcar_pedido_en_preparacion(pedido)[0]
    assert j.listar_cuentas_por_cobrar()==[], 'No debe cobrar antes de que Aarón marque Entregado'
    # Simula el resultado de la T27, tarea independiente que desarrollará Aarón.
    with bd.conectar() as c:
        c.execute("UPDATE pedidos SET estado='Entregado' WHERE id=?",(pedido,))
    cuentas=j.listar_cuentas_por_cobrar()
    assert cuentas==[(mesa_id,200,'69.00')],cuentas
    assert j.consultar_cuenta(mesa_id)['total']=='69.00'
    assert j.calcular_cambio('69','50')[0] is False
    assert j.calcular_cambio('69','100')[2]=='31.00'
    assert j.registrar_pago(mesa_id,'Efectivo','50')[0] is False
    assert j.registrar_pago(mesa_id,'Bizum','100')[0] is False
    ok,_,folio=j.registrar_pago(mesa_id,'Efectivo','100')
    assert ok
    ticket=j.generar_texto_ticket(folio)
    assert 'Taco de prueba' in ticket and 'Cambio: $31.00' in ticket and 'Total: $69.00' in ticket
    assert j.listar_cuentas_por_cobrar()==[]
    assert j.registrar_pago(mesa_id,'Efectivo','100')[0] is False,'No permitir cobro duplicado'
    assert bd.modificar_producto(prod_id,'Taco modificado','',99)[0]
    assert 'Taco de prueba' in j.generar_texto_ticket(folio),'Ticket histórico debe permanecer igual'
    assert j.registrar_proveedor('Abarrotes Norte','8123456789','compras@ejemplo.com')[0]
    assert j.listar_proveedores()[0][1]=='Abarrotes Norte'
    assert not j.registrar_proveedor('')[0]
    assert not j.registrar_proveedor('Otro','','correo-invalido')[0]
    # Pago con tarjeta: sin captura de datos sensibles ni cálculo de cambio.
    assert bd.registrar_mesa(201)[0]
    mesa2=next(x[0] for x in bd.listar_mesas() if x[1]==201)
    ok,_,pedido2=bd.crear_pedido(mesa2)
    assert ok
    assert bd.agregar_producto_pedido(pedido2,prod_id,1)[0]
    with bd.conectar() as c:
        c.execute("UPDATE pedidos SET estado='Entregado' WHERE id=?",(pedido2,))
    ok,_,folio2=j.registrar_pago(mesa2,'Tarjeta')
    assert ok
    assert 'Método: Tarjeta' in j.generar_texto_ticket(folio2)
    assert 'Cambio: $0.00' in j.generar_texto_ticket(folio2)
    print('OK: T31 (efectivo, tarjeta, cobro único), T32, T33 y T41. Base original intacta.')
