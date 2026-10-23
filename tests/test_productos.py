import unittest
from unittest.mock import patch

from controller import productos_controller
from view.main.main import MainView


class ProductosControllerTests(unittest.TestCase):
    def test_registro_incompleto_no_llama_modelo(self):
        with patch.object(productos_controller.productos_model, "crear_producto") as crear:
            respuesta = productos_controller.registrar_producto(1, "", "Producto", "", 1, 1, "10")
        self.assertFalse(respuesta["ok"])
        crear.assert_not_called()

    def test_actualizacion_envia_datos_normalizados(self):
        with patch.object(productos_controller.productos_model, "actualizar_producto") as actualizar:
            respuesta = productos_controller.actualizar_producto(
                1, " p010 ", " Producto nuevo ", " https://ejemplo.com/p010.png ",
                1, 2, "12.50", "ACTIVO"
            )
        self.assertTrue(respuesta["ok"])
        argumentos = actualizar.call_args.args
        self.assertEqual(argumentos[:6], (1, "P010", "Producto nuevo", "https://ejemplo.com/p010.png", 1, 2))
        self.assertEqual(str(argumentos[6]), "12.50")
        self.assertEqual(argumentos[7], "ACTIVO")

    def test_eliminar_producto_fisicamente_por_codigo(self):
        with patch.object(productos_controller.productos_model, "eliminar_producto") as eliminar:
            respuesta = productos_controller.eliminar_producto(1, " p010 ")
        self.assertTrue(respuesta["ok"])
        eliminar.assert_called_once_with(1, "P010")


class ValidacionesGuiTests(unittest.TestCase):
    def test_cantidad_solo_admite_enteros_positivos_sin_signo(self):
        self.assertTrue(MainView._permitir_entero(""))
        self.assertTrue(MainView._permitir_entero("125"))
        self.assertFalse(MainView._permitir_entero("12.5"))
        self.assertFalse(MainView._permitir_entero("-2"))
        self.assertFalse(MainView._permitir_entero("doce"))

    def test_precio_admite_hasta_dos_decimales(self):
        self.assertTrue(MainView._permitir_precio(""))
        self.assertTrue(MainView._permitir_precio("12"))
        self.assertTrue(MainView._permitir_precio("12."))
        self.assertTrue(MainView._permitir_precio("12.50"))
        self.assertFalse(MainView._permitir_precio(".50"))
        self.assertFalse(MainView._permitir_precio("12.500"))
        self.assertFalse(MainView._permitir_precio("-1"))


if __name__ == "__main__":
    unittest.main()
