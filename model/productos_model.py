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


def listar_productos():
    with _cursor() as (_, cursor):
        cursor.execute("""
            SELECT p.codigo, p.id_unidad, p.id_presentacion, p.descripcion, p.imagen_url,
                   um.nombre AS unidad_medida,
                   pr.nombre AS presentacion, p.precio, p.estado,
                   p.fecha_registro
            FROM productos p
            INNER JOIN unidades_medida um ON um.id_unidad = p.id_unidad
            INNER JOIN presentaciones pr ON pr.id_presentacion = p.id_presentacion
            ORDER BY p.codigo
        """)
        return cursor.fetchall()


def _validar_gestor_productos(cursor, id_usuario):
    cursor.execute("""
        SELECT r.nombre AS rol
        FROM usuarios u
        INNER JOIN roles r ON r.id_rol = u.id_rol
        WHERE u.id_usuario = %s AND u.estado = 'ACTIVO'
    """, (id_usuario,))
    usuario = cursor.fetchone()
    if usuario is None or usuario["rol"].lower() not in ("admin", "operador"):
        raise PermissionError("No tiene permiso para gestionar productos.")


def _validar_catalogos(cursor, id_unidad, id_presentacion):
    cursor.execute("SELECT id_unidad FROM unidades_medida WHERE id_unidad = %s", (id_unidad,))
    if cursor.fetchone() is None:
        raise ValueError("Seleccione una unidad de medida válida.")
    cursor.execute("SELECT id_presentacion FROM presentaciones WHERE id_presentacion = %s", (id_presentacion,))
    if cursor.fetchone() is None:
        raise ValueError("Seleccione una presentación válida.")


def crear_producto(id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio):
    with _cursor() as (conexion, cursor):
        try:
            _validar_gestor_productos(cursor, id_usuario)
            _validar_catalogos(cursor, id_unidad, id_presentacion)
            cursor.execute("""
                INSERT INTO productos (
                    codigo, id_unidad, id_presentacion, descripcion, imagen_url, precio, fecha_registro
                ) VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
            """, (codigo, id_unidad, id_presentacion, descripcion, imagen_url, precio))
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise


def actualizar_producto(id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio, estado):
    with _cursor() as (conexion, cursor):
        try:
            _validar_gestor_productos(cursor, id_usuario)
            _validar_catalogos(cursor, id_unidad, id_presentacion)
            cursor.execute("SELECT codigo FROM productos WHERE codigo = %s", (codigo,))
            if cursor.fetchone() is None:
                raise ValueError("El producto seleccionado ya no existe.")
            cursor.execute("""
                UPDATE productos
                SET descripcion = %s, imagen_url = %s, id_unidad = %s, id_presentacion = %s,
                    precio = %s, estado = %s
                WHERE codigo = %s
            """, (descripcion, imagen_url, id_unidad, id_presentacion, precio, estado, codigo))
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise


def eliminar_producto(id_usuario, codigo):
    with _cursor() as (conexion, cursor):
        try:
            _validar_gestor_productos(cursor, id_usuario)
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM inventario_movimientos
                WHERE codigo_producto = %s
            """, (codigo,))
            if cursor.fetchone()["total"]:
                raise ValueError(
                    "No se puede eliminar el producto porque tiene movimientos de inventario."
                )
            cursor.execute("""
                DELETE FROM productos
                WHERE codigo = %s
            """, (codigo,))
            if cursor.rowcount == 0:
                raise ValueError("El producto seleccionado ya no existe.")
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
