import unittest
from unittest.mock import MagicMock, patch

from controller import usuarios_controller as registro

modelo = registro.usuarios_model


class RegistroTests(unittest.TestCase):
    def test_validaciones_no_escriben(self):
        with patch.object(modelo, 'crear_usuario') as crear:
            for nombre, usuario, password, confirmar, rol in (
                ('', 'ana', 'abcdefgh', 'abcdefgh', 1),
                ('Ana', 'a' * 51, 'abcdefgh', 'abcdefgh', 1),
                ('Ana', 'ana', 'corta', 'corta', 1),
                ('Ana', 'ana', 'abcdefgh', 'diferente', 1),
                ('Ana', 'ana', 'abcdefgh', 'abcdefgh', None),
            ):
                self.assertFalse(registro.registrar_usuario(1, nombre, usuario, password, confirmar, rol)['ok'])
            crear.assert_not_called()

    def test_duplicado(self):
        error = Exception('duplicate')
        error.errno = 1062
        with patch.object(modelo, 'crear_usuario', side_effect=error):
            respuesta = registro.registrar_usuario(1, 'Ana', 'ana', 'abcdefgh', 'abcdefgh', 2)
        self.assertFalse(respuesta['ok'])
        self.assertIn('ya existe', respuesta['mensaje'])

    def test_hash_y_compatibilidad(self):
        password = ' abcdefgh '
        hashed = modelo._hash_password(password)
        self.assertNotEqual(hashed, password)
        self.assertTrue(modelo._verificar_password(password, hashed))
        self.assertFalse(modelo._verificar_password(password.strip(), hashed))
        self.assertTrue(modelo._verificar_password('anterior', 'anterior'))
        self.assertFalse(modelo._verificar_password('incorrecta', 'anterior'))

    def test_guardado_y_login(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.side_effect = [{'id_usuario': 1}, {'id_rol': 2}]
        cursor.lastrowid = 42
        with patch.object(modelo, 'obtener_conexion', return_value=conexion):
            self.assertEqual(modelo.crear_usuario(1, 'Ana', 'ana', 'abcdefgh', 2), 42)
            parametros = cursor.execute.call_args.args[1]
            self.assertTrue(modelo._verificar_password('abcdefgh', parametros[2]))
            conexion.commit.assert_called_once()
            cursor.fetchone.side_effect = None
            cursor.fetchone.return_value = {'id_usuario': 42, 'password_hash': parametros[2], 'rol': 'Operador'}
            self.assertEqual(modelo.buscar_usuario_login('ana', 'abcdefgh')['id_usuario'], 42)
            cursor.fetchone.return_value = {'id_usuario': 42, 'password_hash': parametros[2]}
            self.assertIsNone(modelo.buscar_usuario_login('ana', 'incorrecta'))
        self.assertEqual(conexion.close.call_count, 3)

    def test_registro_publico_sin_elegir_rol(self):
        with patch.object(modelo, 'crear_cuenta') as crear:
            respuesta = registro.registrar_cuenta(' Ana ', ' ana ', 'abcdefgh', 'abcdefgh')
        self.assertTrue(respuesta['ok'])
        crear.assert_called_once_with('Ana', 'ana', 'abcdefgh')

    def test_registro_publico_asigna_operador(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = {'id_rol': 7}
        with patch.object(modelo, 'obtener_conexion', return_value=conexion):
            modelo.crear_cuenta('Ana', 'ana', 'abcdefgh')
        self.assertIn("LOWER(nombre) = 'operador'", cursor.execute.call_args_list[0].args[0])
        self.assertEqual(cursor.execute.call_args.args[1][0], 7)
        conexion.commit.assert_called_once()

    def test_sin_rol_operador_no_guarda(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = None
        with patch.object(modelo, 'obtener_conexion', return_value=conexion):
            with self.assertRaises(ValueError):
                modelo.crear_cuenta('Ana', 'ana', 'abcdefgh')
        conexion.commit.assert_not_called()
        conexion.rollback.assert_called_once()

    def test_no_admin_no_inserta(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = None
        with patch.object(modelo, 'obtener_conexion', return_value=conexion):
            with self.assertRaises(PermissionError):
                modelo.crear_usuario(2, 'Ana', 'ana', 'abcdefgh', 2)
        conexion.commit.assert_not_called()
        conexion.rollback.assert_called_once()
        self.assertEqual(cursor.execute.call_count, 1)
        conexion.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
