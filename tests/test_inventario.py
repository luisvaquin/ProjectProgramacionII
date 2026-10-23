import unittest
from unittest.mock import patch

from controller import inventario_controller


class InventarioControllerTests(unittest.TestCase):
    def test_no_registra_cantidad_invalida(self):
        with patch.object(inventario_controller.inventario_model, "registrar_movimiento") as registrar:
            respuesta = inventario_controller.registrar_movimiento(
                1, "P001", "ENTRADA", "0", "", None
            )
        self.assertFalse(respuesta["ok"])
        registrar.assert_not_called()

    def test_ajuste_requiere_direccion(self):
        with patch.object(inventario_controller.inventario_model, "registrar_movimiento") as registrar:
            respuesta = inventario_controller.registrar_movimiento(
                1, "P001", "AJUSTE", "2", "Conteo físico", None
            )
        self.assertFalse(respuesta["ok"])
        self.assertIn("suma o resta", respuesta["mensaje"])
        registrar.assert_not_called()

    def test_salida_se_envia_al_modelo(self):
        with patch.object(inventario_controller.inventario_model, "registrar_movimiento") as registrar:
            respuesta = inventario_controller.registrar_movimiento(
                1, " p001 ", "salida", "3", "Venta", None
            )
        self.assertTrue(respuesta["ok"])
        registrar.assert_called_once_with(1, "P001", "SALIDA", 3, "Venta", None)

    def test_reporte_valida_fecha(self):
        with patch.object(inventario_controller.inventario_model, "listar_reporte_inventario") as listar:
            respuesta = inventario_controller.obtener_reporte_inventario(fecha="20/10/2026")
        self.assertFalse(respuesta["ok"])
        self.assertIn("AAAA-MM-DD", respuesta["mensaje"])
        listar.assert_not_called()

    def test_reporte_envia_filtros_combinados(self):
        with patch.object(
            inventario_controller.inventario_model,
            "listar_reporte_inventario",
            return_value=[],
        ) as listar:
            respuesta = inventario_controller.obtener_reporte_inventario(
                "p004", "cereal", "2026-10-20"
            )
        self.assertTrue(respuesta["ok"])
        listar.assert_called_once_with("P004", "cereal", "2026-10-20")

    def test_dashboard_reune_resumen_y_actividad(self):
        resumen = {"productos_activos": 2, "existencia_total": 10, "movimientos_recientes": 1}
        with patch.object(inventario_controller.inventario_model, "obtener_resumen_dashboard", return_value=resumen), \
             patch.object(inventario_controller.inventario_model, "listar_actividad_reciente", return_value=[]):
            respuesta = inventario_controller.obtener_resumen_dashboard()
        self.assertTrue(respuesta["ok"])
        self.assertEqual(respuesta["resumen"], resumen)


if __name__ == "__main__":
    unittest.main()
