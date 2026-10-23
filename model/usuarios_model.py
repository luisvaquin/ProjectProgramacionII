import hashlib
import hmac
import secrets
from contextlib import contextmanager

from model.conexion import obtener_conexion


@contextmanager
def _cursor():
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        yield conexion, cursor
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def _hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000)
    return f"pbkdf2_sha256$600000${salt}${digest.hex()}"


def _verificar_password(password, almacenado):
    if not almacenado.startswith("pbkdf2_sha256$"):
        # Compatibilidad con las cuentas existentes del proyecto.
        return hmac.compare_digest(password.encode(), almacenado.encode())
    try:
        _, vueltas, salt, esperado = almacenado.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(vueltas))
        return hmac.compare_digest(digest.hex(), esperado)
    except (ValueError, TypeError, OverflowError):
        return False


def buscar_usuario_login(usuario, password):
    with _cursor() as (_, cursor):
        cursor.execute("""
            SELECT u.id_usuario, u.usuario, u.nombre_completo, u.estado,
                   u.password_hash, r.nombre AS rol
            FROM usuarios u INNER JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.usuario = %s AND u.estado = 'ACTIVO' LIMIT 1
        """, (usuario,))
        resultado = cursor.fetchone()
    if resultado is None:
        return None
    password_hash = resultado.pop("password_hash")
    return resultado if _verificar_password(password, password_hash) else None


def listar_roles():
    with _cursor() as (_, cursor):
        cursor.execute("SELECT id_rol, nombre FROM roles ORDER BY nombre")
        return cursor.fetchall()


def listar_usuarios():
    with _cursor() as (_, cursor):
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_completo, u.usuario, u.estado,
                   r.nombre AS rol, u.fecha_creacion
            FROM usuarios u
            INNER JOIN roles r ON r.id_rol = u.id_rol
            ORDER BY u.id_usuario
        """)
        return cursor.fetchall()


def _validar_administrador(cursor, id_administrador):
    cursor.execute("""
        SELECT u.id_usuario FROM usuarios u
        INNER JOIN roles r ON r.id_rol = u.id_rol
        WHERE u.id_usuario = %s AND u.estado = 'ACTIVO'
        AND LOWER(r.nombre) = 'admin' FOR UPDATE
    """, (id_administrador,))
    if cursor.fetchone() is None:
        raise PermissionError("Solo un administrador activo puede gestionar usuarios.")


def actualizar_usuario(id_administrador, id_usuario, nombre, usuario, id_rol, estado):
    with _cursor() as (conexion, cursor):
        try:
            _validar_administrador(cursor, id_administrador)
            if id_administrador == id_usuario and estado == "INACTIVO":
                raise ValueError("No puede inactivar su propia cuenta.")
            cursor.execute("SELECT id_rol FROM roles WHERE id_rol = %s", (id_rol,))
            if cursor.fetchone() is None:
                raise ValueError("Seleccione un rol válido.")
            cursor.execute("""
                SELECT id_usuario FROM usuarios
                WHERE usuario = %s AND id_usuario <> %s
            """, (usuario, id_usuario))
            if cursor.fetchone() is not None:
                raise ValueError("Ese nombre de usuario ya existe. Elija otro.")
            cursor.execute("""
                UPDATE usuarios
                SET nombre_completo = %s, usuario = %s, id_rol = %s, estado = %s
                WHERE id_usuario = %s
            """, (nombre, usuario, id_rol, estado, id_usuario))
            if cursor.rowcount == 0:
                raise ValueError("El usuario seleccionado ya no existe.")
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise


def inactivar_usuario(id_administrador, id_usuario):
    with _cursor() as (conexion, cursor):
        try:
            _validar_administrador(cursor, id_administrador)
            if id_administrador == id_usuario:
                raise ValueError("No puede inactivar su propia cuenta.")
            cursor.execute("""
                UPDATE usuarios SET estado = 'INACTIVO'
                WHERE id_usuario = %s AND estado = 'ACTIVO'
            """, (id_usuario,))
            if cursor.rowcount == 0:
                raise ValueError("El usuario no existe o ya está inactivo.")
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise


def crear_usuario(id_administrador, nombre, usuario, password, id_rol):
    password_hash = _hash_password(password)
    with _cursor() as (conexion, cursor):
        try:
            _validar_administrador(cursor, id_administrador)
            cursor.execute("SELECT id_rol FROM roles WHERE id_rol = %s", (id_rol,))
            if cursor.fetchone() is None:
                raise ValueError("Seleccione un rol válido.")
            cursor.execute("""
                INSERT INTO usuarios (id_rol, usuario, password_hash, nombre_completo)
                VALUES (%s, %s, %s, %s)
            """, (id_rol, usuario, password_hash, nombre))
            id_usuario = cursor.lastrowid
            conexion.commit()
            return id_usuario
        except Exception:
            conexion.rollback()
            raise


def crear_cuenta(nombre, usuario, password):
    """El registro público siempre asigna Operador desde la base de datos."""
    password_hash = _hash_password(password)
    with _cursor() as (conexion, cursor):
        try:
            cursor.execute("SELECT id_rol FROM roles WHERE LOWER(nombre) = 'operador'")
            rol = cursor.fetchone()
            if rol is None:
                raise ValueError("El registro no está disponible: falta configurar el rol Operador.")
            cursor.execute("""
                INSERT INTO usuarios (id_rol, usuario, password_hash, nombre_completo)
                VALUES (%s, %s, %s, %s)
            """, (rol["id_rol"], usuario, password_hash, nombre))
            id_usuario = cursor.lastrowid
            conexion.commit()
            return id_usuario
        except Exception:
            conexion.rollback()
            raise
