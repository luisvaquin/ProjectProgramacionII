import mysql.connector


def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="luis",
        password="admin",
        database="dbProyecto",
    )
