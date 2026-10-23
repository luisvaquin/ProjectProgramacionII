from model import usuarios_model


def obtener_roles():
    try:
        roles = usuarios_model.listar_roles()
        return {"ok": bool(roles), "roles": roles,
                "mensaje": "" if roles else "No hay roles configurados en la base de datos."}
    except Exception:
        return {"ok": False, "roles": [], "mensaje": "No se pudieron cargar los roles. Revise la conexión con MySQL."}


def obtener_usuarios():
    try:
        return {"ok": True, "usuarios": usuarios_model.listar_usuarios(), "mensaje": ""}
    except Exception:
        return {
            "ok": False,
            "usuarios": [],
            "mensaje": "No se pudieron cargar los usuarios. Revise la conexión con MySQL.",
        }


def registrar_usuario(id_administrador, nombre, usuario, password, confirmacion, id_rol):
    nombre, usuario = nombre.strip(), usuario.strip()
    mensaje = None
    if not nombre or not usuario or not password or not confirmacion:
        mensaje = "Complete todos los campos."
    elif len(nombre) > 100 or len(usuario) > 50:
        mensaje = "El nombre admite hasta 100 caracteres y el usuario hasta 50."
    elif len(password) < 8 or len(password) > 128:
        mensaje = "La contraseña debe tener entre 8 y 128 caracteres."
    elif password != confirmacion:
        mensaje = "Las contraseñas no coinciden."
    elif id_administrador is not None and not id_rol:
        mensaje = "Seleccione un rol."
    if mensaje:
        return {"ok": False, "mensaje": mensaje}
    try:
        if id_administrador is None:
            usuarios_model.crear_cuenta(nombre, usuario, password)
        else:
            usuarios_model.crear_usuario(id_administrador, nombre, usuario, password, id_rol)
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception as error:
        mensaje = ("Ese nombre de usuario ya existe. Elija otro."
                   if getattr(error, "errno", None) == 1062
                   else "No se pudo guardar el usuario. Revise la conexión con MySQL.")
        return {"ok": False, "mensaje": mensaje}
    return {"ok": True, "mensaje": "Usuario registrado correctamente."}


def registrar_cuenta(nombre, usuario, password, confirmacion):
    return registrar_usuario(None, nombre, usuario, password, confirmacion, None)


def actualizar_usuario(id_administrador, id_usuario, nombre, usuario, id_rol, estado):
    nombre, usuario = nombre.strip(), usuario.strip()
    if not nombre or not usuario:
        return {"ok": False, "mensaje": "Complete nombre y usuario."}
    if len(nombre) > 100 or len(usuario) > 50:
        return {"ok": False, "mensaje": "El nombre admite hasta 100 caracteres y el usuario hasta 50."}
    if not id_rol or estado not in ("ACTIVO", "INACTIVO"):
        return {"ok": False, "mensaje": "Seleccione un rol y estado válidos."}
    try:
        usuarios_model.actualizar_usuario(
            id_administrador, id_usuario, nombre, usuario, id_rol, estado
        )
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception:
        return {"ok": False, "mensaje": "No se pudo actualizar el usuario. Revise la conexión con MySQL."}
    return {"ok": True, "mensaje": "Usuario actualizado correctamente."}


def eliminar_usuario(id_administrador, id_usuario):
    try:
        usuarios_model.inactivar_usuario(id_administrador, id_usuario)
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception:
        return {"ok": False, "mensaje": "No se pudo inactivar el usuario. Revise la conexión con MySQL."}
    return {"ok": True, "mensaje": "Usuario inactivado correctamente."}
