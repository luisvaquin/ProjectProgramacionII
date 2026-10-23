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


def _expresion_existencia():
    return """
        COALESCE(SUM(
            CASE
                WHEN tipo_movimiento = 'ENTRADA' THEN cantidad
                WHEN tipo_movimiento = 'SALIDA' THEN -cantidad
                WHEN direccion_ajuste = 'RESTA' THEN -cantidad
                ELSE cantidad
            END
        ), 0)
    """


def listar_productos_inventario():
    with _cursor() as (_, cursor):
        cursor.execute(f"""
            SELECT p.codigo, p.descripcion, um.nombre AS unidad_medida,
                   pr.nombre AS presentacion, {_expresion_existencia()} AS existencia
            FROM productos p
            INNER JOIN unidades_medida um ON um.id_unidad = p.id_unidad
            INNER JOIN presentaciones pr ON pr.id_presentacion = p.id_presentacion
            LEFT JOIN inventario_movimientos im ON im.codigo_producto = p.codigo
            WHERE p.estado = 'ACTIVO'
            GROUP BY p.codigo, p.descripcion, um.nombre, pr.nombre
            ORDER BY p.codigo
        """)
        return cursor.fetchall()


def listar_movimientos():
    with _cursor() as (_, cursor):
        cursor.execute("""
            SELECT im.id_movimiento, im.codigo_producto, p.descripcion,
                   im.tipo_movimiento, im.direccion_ajuste, im.cantidad,
                   im.fecha, im.observacion, u.nombre_completo AS usuario
            FROM inventario_movimientos im
            INNER JOIN productos p ON p.codigo = im.codigo_producto
            INNER JOIN usuarios u ON u.id_usuario = im.id_usuario
            ORDER BY im.fecha_creacion DESC, im.id_movimiento DESC
        """)
        return cursor.fetchall()


def obtener_resumen_dashboard():
    with _cursor() as (_, cursor):
        cursor.execute("SELECT COUNT(*) AS productos_activos FROM productos WHERE estado = 'ACTIVO'")
        productos_activos = cursor.fetchone()["productos_activos"]
        cursor.execute(f"""
            SELECT {_expresion_existencia()} AS existencia_total
            FROM inventario_movimientos
        """)
        existencia_total = cursor.fetchone()["existencia_total"]
        cursor.execute("""
            SELECT COUNT(*) AS movimientos_recientes
            FROM inventario_movimientos
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        movimientos_recientes = cursor.fetchone()["movimientos_recientes"]
        return {
            "productos_activos": productos_activos,
            "existencia_total": existencia_total,
            "movimientos_recientes": movimientos_recientes,
        }


def listar_actividad_reciente():
    with _cursor() as (_, cursor):
        cursor.execute("""
            SELECT im.codigo_producto, p.descripcion, im.tipo_movimiento,
                   im.direccion_ajuste, im.cantidad, im.fecha
            FROM inventario_movimientos im
            INNER JOIN productos p ON p.codigo = im.codigo_producto
            ORDER BY im.fecha_creacion DESC, im.id_movimiento DESC
            LIMIT 5
        """)
        return cursor.fetchall()


def listar_reporte_inventario(codigo=None, descripcion=None, fecha=None):
    """Devuelve una fila por producto con su existencia actual calculada."""
    condiciones = []
    parametros = []
    if codigo:
        condiciones.append("p.codigo = %s")
        parametros.append(codigo)
    if descripcion:
        condiciones.append("p.descripcion LIKE %s")
        parametros.append(f"%{descripcion}%")
    if fecha:
        condiciones.append("p.fecha_registro = %s")
        parametros.append(fecha)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    with _cursor() as (_, cursor):
        cursor.execute(f"""
            SELECT p.codigo, p.fecha_registro AS fecha, p.descripcion,
                   {_expresion_existencia()} AS cantidad,
                   pr.nombre AS presentacion, um.nombre AS unidad_medida, p.precio
            FROM productos p
            INNER JOIN presentaciones pr ON pr.id_presentacion = p.id_presentacion
            INNER JOIN unidades_medida um ON um.id_unidad = p.id_unidad
            LEFT JOIN inventario_movimientos im ON im.codigo_producto = p.codigo
            {where}
            GROUP BY p.codigo, p.fecha_registro, p.descripcion, pr.nombre, um.nombre, p.precio
            ORDER BY p.codigo
        """, tuple(parametros))
        return cursor.fetchall()


def registrar_movimiento(id_usuario, codigo_producto, tipo_movimiento, cantidad,
                         observacion, direccion_ajuste=None):
    with _cursor() as (conexion, cursor):
        try:
            cursor.execute("""
                SELECT r.nombre AS rol
                FROM usuarios u
                INNER JOIN roles r ON r.id_rol = u.id_rol
                WHERE u.id_usuario = %s AND u.estado = 'ACTIVO'
            """, (id_usuario,))
            usuario = cursor.fetchone()
            if usuario is None or usuario["rol"].lower() not in ("admin", "operador"):
                raise PermissionError("No tiene permiso para registrar movimientos.")

            # Bloqueamos el producto mientras se calcula y registra una salida.
            cursor.execute("""
                SELECT codigo FROM productos
                WHERE codigo = %s AND estado = 'ACTIVO' FOR UPDATE
            """, (codigo_producto,))
            if cursor.fetchone() is None:
                raise ValueError("Seleccione un producto activo válido.")

            if tipo_movimiento in ("SALIDA", "AJUSTE") and direccion_ajuste != "SUMA":
                cursor.execute(f"""
                    SELECT {_expresion_existencia()} AS existencia
                    FROM inventario_movimientos
                    WHERE codigo_producto = %s
                """, (codigo_producto,))
                existencia = cursor.fetchone()["existencia"]
                if cantidad > existencia:
                    raise ValueError(
                        f"Existencia insuficiente. Disponible: {existencia}."
                    )

            cursor.execute("""
                INSERT INTO inventario_movimientos (
                    codigo_producto, id_usuario, tipo_movimiento, direccion_ajuste,
                    cantidad, fecha, observacion
                ) VALUES (%s, %s, %s, %s, %s, CURDATE(), %s)
            """, (
                codigo_producto, id_usuario, tipo_movimiento, direccion_ajuste,
                cantidad, observacion or None,
            ))
            conexion.commit()
            return cursor.lastrowid
        except Exception:
            conexion.rollback()
            raise
