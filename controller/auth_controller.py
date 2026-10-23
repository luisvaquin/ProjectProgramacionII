from model import usuarios_model


def validar_login(usuario, password):
    usuario = usuario.strip()

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
