"""Sprint 4, T64 (Said Jesús): prueba aislada de activación/desactivación.
Corrección y prueba elaboradas con asistencia de IA. No modifica restaurante.db.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import base_datos


class TestReactivacionT64(unittest.TestCase):
    def test_reactivar_y_recuperar_acceso(self):
        with tempfile.TemporaryDirectory() as temporal:
            with patch.object(base_datos, 'NOMBRE_BD', str(Path(temporal) / 'pruebas.db')):
                base_datos.inicializar_base_de_datos()
                self.assertFalse(base_datos.activar_empleado(1)[0])
                base_datos.desactivar_empleado(1)
                self.assertIsNone(base_datos.validar_credenciales('gerente1', 'admin123'))
                self.assertTrue(base_datos.activar_empleado(1)[0])
                self.assertIsNotNone(base_datos.validar_credenciales('gerente1', 'admin123'))
                self.assertFalse(base_datos.activar_empleado(1)[0])
                self.assertFalse(base_datos.activar_empleado(99999)[0])


if __name__ == '__main__':
    unittest.main()
