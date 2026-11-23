"""Pruebas reproducibles de T47 sin restaurante.db ni módulos de terceros."""
import unittest
from unittest.mock import Mock
from javier_t47_fechas import validar_rango_t47, enviar_rango_validado_t47


class TestFechasT47(unittest.TestCase):
    def test_rango_normal(self):
        self.assertEqual(validar_rango_t47("2026-11-01", "2026-11-20"), ("2026-11-01", "2026-11-20"))

    def test_dia_unico_inclusivo(self):
        self.assertEqual(validar_rango_t47("2026-11-20", "2026-11-20"), ("2026-11-20", "2026-11-20"))

    def test_rango_invertido(self):
        with self.assertRaisesRegex(ValueError, "posterior"):
            validar_rango_t47("2026-11-21", "2026-11-20")

    def test_fecha_imposible(self):
        with self.assertRaisesRegex(ValueError, "no es válida"):
            validar_rango_t47("2026-02-30", "2026-03-01")

    def test_formato_incorrecto(self):
        with self.assertRaisesRegex(ValueError, "formato"):
            validar_rango_t47("20/11/2026", "2026-11-20")

    def test_campos_vacios(self):
        with self.assertRaisesRegex(ValueError, "formato"):
            validar_rango_t47("", "2026-11-20")

    def test_el_callback_recibe_ambas_fechas(self):
        simulacion = Mock(return_value="respuesta de prueba")
        resultado = enviar_rango_validado_t47("2026-11-01", "2026-11-20", simulacion)
        simulacion.assert_called_once_with("2026-11-01", "2026-11-20")
        self.assertEqual(resultado, "respuesta de prueba")

    def test_no_invoca_callback_si_rango_invalido(self):
        simulacion = Mock()
        with self.assertRaises(ValueError):
            enviar_rango_validado_t47("2026-11-21", "2026-11-20", simulacion)
        simulacion.assert_not_called()

    def test_no_admite_callback_ausente(self):
        with self.assertRaises(TypeError):
            enviar_rango_validado_t47("2026-11-01", "2026-11-20", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
