"""Pruebas sobre SQLite temporal. Ejecutar con python -m unittest -v pruebas_juan_said_sprint4"""
import os,sys,tempfile,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'Sistema_Comandas_Sprint3_Completo'))
sys.path.insert(0,os.path.dirname(__file__))
import base_datos
from javier_caja_proveedores import preparar_tablas_javier,registrar_pago
from sprint3_nuevo import marcar_listo,marcar_entregado
import juan_sprint4 as j
import said_sprint4 as s

class TestSprint4(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        base_datos.NOMBRE_BD=os.path.join(self.tmp.name,'test.db')
        base_datos.inicializar_base_de_datos();preparar_tablas_javier()
        base_datos.registrar_mesa(1)
        self.mesa=base_datos.listar_mesas()[0][0]
        base_datos.registrar_producto('Taco','Platillo','',35)
        self.producto=base_datos.listar_productos()[0][0]
    def tearDown(self):self.tmp.cleanup()
    def cobrar(self):
        ok,_,pid=base_datos.crear_pedido(self.mesa);self.assertTrue(ok)
        self.assertTrue(base_datos.agregar_producto_pedido(pid,self.producto,2)[0])
        self.assertTrue(base_datos.enviar_pedido_cocina(pid)[0])
        self.assertTrue(base_datos.marcar_pedido_en_preparacion(pid)[0])
        self.assertTrue(marcar_listo(pid)[0]);self.assertTrue(marcar_entregado(pid)[0])
        self.assertTrue(registrar_pago(self.mesa,'Tarjeta')[0])
        return pid
    def test_t45_t46_cierre_y_resumen(self):
        self.cobrar()
        self.assertTrue(j.cerrar_mesa_t45(self.mesa)[0])
        r=j.resumen_diario_t46()
        self.assertEqual(r['cantidad'],1);self.assertEqual(str(r['total']),'70.00')
        self.assertFalse(j.cerrar_mesa_t45(self.mesa)[0])
    def test_t45_no_cierra_sin_pago(self):
        self.assertFalse(j.cerrar_mesa_t45(self.mesa)[0])
    def test_t49_t50_filtros(self):
        pid=self.cobrar()
        filas=s.buscar_pedidos_t49(mesa=1,folio=pid)
        self.assertEqual(len(filas),1)
        self.assertEqual(s.buscar_pedidos_t49(mesa=999),[])
        self.assertEqual(s.detalle_historico_t50(pid)['folio'],pid)
    def test_t47_periodo_inclusivo(self):
        self.cobrar();j.cerrar_mesa_t45(self.mesa)
        hoy=__import__('datetime').date.today().isoformat()
        filas,total=j.consultar_ventas_periodo_t45(hoy,hoy)
        self.assertEqual(len(filas),1);self.assertEqual(total,70)
    def test_t49_fecha_invalida(self):
        with self.assertRaises(ValueError):s.buscar_pedidos_t49(fecha='2026-02-30')

if __name__=='__main__':unittest.main()
