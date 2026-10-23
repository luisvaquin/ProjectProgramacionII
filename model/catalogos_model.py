from contextlib import contextmanager

from model.conexion import obtener_conexion


@contextmanager
def _cursor():
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        yield cursor
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def listar_unidades_medida():
    with _cursor() as cursor:
        cursor.execute("SELECT id_unidad, nombre, abreviatura FROM unidades_medida ORDER BY nombre")
        return cursor.fetchall()


def listar_presentaciones():
    with _cursor() as cursor:
        cursor.execute("SELECT id_presentacion, nombre FROM presentaciones ORDER BY nombre")
        return cursor.fetchall()
