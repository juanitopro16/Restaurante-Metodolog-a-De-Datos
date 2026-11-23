"""Pruebas T47/T54/T55 con base SQLite TEMPORAL; no toca restaurante.db.
Ejecutar desde la carpeta del proyecto: python -m unittest -v prueba_javier_sprint4
"""
import os
import tempfile
import unittest
from decimal import Decimal
from unittest.mock import patch

import base_datos
from javier_caja_proveedores import preparar_tablas_javier, registrar_pago
from sprint3_nuevo import marcar_listo, marcar_entregado
from juan_sprint4 import cerrar_mesa_t45, preparar_ventas_t45
import javier_sprint4 as j


class TestJavierSprint4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.original = base_datos.NOMBRE_BD
        base_datos.NOMBRE_BD = os.path.join(cls.temp.name, 'temporal_javier.db')
        base_datos.inicializar_base_de_datos()
        preparar_tablas_javier()
        preparar_ventas_t45()
        base_datos.registrar_mesa(10)
        cls.mesa = next(m[0] for m in base_datos.listar_mesas() if m[1] == 10)
        base_datos.registrar_producto('Taco', 'Platillo', '', 35)
        cls.producto = next(p[0] for p in base_datos.listar_productos() if p[1] == 'Taco')
        ok, _, cls.pedido = base_datos.crear_pedido(cls.mesa)
        assert ok
        ok, _ = base_datos.agregar_producto_pedido(cls.pedido, cls.producto, 2, 'sin salsa')
        assert ok
        ok, _ = base_datos.enviar_pedido_cocina(cls.pedido)
        assert ok
        ok, _ = base_datos.marcar_pedido_en_preparacion(cls.pedido)
        assert ok
        ok, _ = marcar_listo(cls.pedido)
        assert ok
        ok, _ = marcar_entregado(cls.pedido)
        assert ok
        ok, _, cls.pago = registrar_pago(cls.mesa, 'Efectivo', '100')
        assert ok
        ok, _ = cerrar_mesa_t45(cls.mesa)
        assert ok

    @classmethod
    def tearDownClass(cls):
        base_datos.NOMBRE_BD = cls.original
        cls.temp.cleanup()

    def test_t47_periodo_contiene_venta(self):
        with base_datos.conectar() as c:
            dia = c.execute('SELECT substr(fecha_cierre,1,10) FROM ventas_cierre_s4').fetchone()[0]
        datos = j.consultar_periodo_t47(dia, dia)
        self.assertEqual(datos['cantidad'], 1)
        self.assertEqual(datos['total'], Decimal('70.00'))

    def test_t47_fechas_invertidas(self):
        with self.assertRaises(ValueError):
            j.consultar_periodo_t47('2026-11-22', '2026-11-21')

    def test_t47_periodo_sin_ventas(self):
        datos = j.consultar_periodo_t47('2020-01-01', '2020-01-02')
        self.assertEqual(datos['cantidad'], 0)
        self.assertEqual(datos['total'], Decimal('0.00'))

    def test_t55_dia(self):
        with base_datos.conectar() as c:
            dia = c.execute('SELECT substr(fecha_cierre,1,10) FROM ventas_cierre_s4').fetchone()[0]
        datos = j.consultar_dia_t55(dia)
        self.assertEqual(datos['cantidad'], 1)
        self.assertEqual(datos['total'], Decimal('70.00'))

    def test_t54_ticket_historico(self):
        ticket = j.texto_ticket_t54(self.pago)
        self.assertIn('Folio de pago:', ticket)
        self.assertIn('2 x Taco', ticket)
        self.assertIn('$70.00', ticket)
        self.assertIn('Cambio:   $30.00', ticket)

    def test_t54_ticket_inexistente(self):
        self.assertIsNone(j.texto_ticket_t54(9999999))

    def test_t54_no_depende_precio_actual(self):
        antes = j.texto_ticket_t54(self.pago)
        base_datos.modificar_producto(self.producto, 'Taco', '', 90)
        despues = j.texto_ticket_t54(self.pago)
        self.assertEqual(antes, despues)

    def test_t53_reutiliza_api_existente(self):
        self.assertTrue(callable(j.mostrar_caja_t53))
        self.assertTrue(callable(j.registrar_pago))


if __name__ == '__main__':
    unittest.main(verbosity=2)
