from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USUARIOS_MODEL_PATH = PROJECT_ROOT / "model" / "usuarios.model" / "usuarios.model.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _cargar_modulo(nombre, ruta):
    spec = spec_from_file_location(nombre, ruta)
    modulo = module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


usuarios_model = _cargar_modulo("usuarios_model", USUARIOS_MODEL_PATH)


def validar_login(usuario, password):
    usuario = usuario.strip()
    password = password.strip()

    if not usuario or not password:
        return {
            "ok": False,
            "mensaje": "Ingrese usuario y contraseña.",
            "usuario": None,
        }

    try:
        usuario_encontrado = usuarios_model.buscar_usuario_login(usuario, password)
    except Exception as error:
        return {
            "ok": False,
            "mensaje": f"No se pudo conectar con la base de datos: {error}",
            "usuario": None,
        }

    if usuario_encontrado is None:
        return {
            "ok": False,
            "mensaje": "Usuario o contraseña incorrectos, intente de nuevo",
            "usuario": None,
        }

    return {
        "ok": True,
        "mensaje": "Inicio de sesión correcto.",
        "usuario": usuario_encontrado,
    }
