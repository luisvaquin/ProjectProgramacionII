from model.conexion import obtener_conexion


def buscar_usuario_login(usuario, password):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
        SELECT
            u.id_usuario,
            u.usuario,
            u.nombre_completo,
            u.estado,
            r.nombre AS rol
        FROM usuarios u
        INNER JOIN roles r ON r.id_rol = u.id_rol
        WHERE u.usuario = %s
          AND u.password_hash = %s
          AND u.estado = 'ACTIVO'
        LIMIT 1;
    """

    cursor.execute(consulta, (usuario, password))
    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado
