# Proyecto Luis Rodrigo Vaquin

## Comprender el proyecto
Controlar quien ingresa al sistema, que productos maneja la empresa, que existencia hay en inventario y permitir la consulta o generacion de reportes de forma ordenada.

## Tablas db
- `roles`: define el tipo de usuario dentro del sistema.
- `usuarios`: guarda los datos de acceso y estado del usuario.
- `unidades_medida`: catalogo de unidades como Unidades, Libras o Kilogramos.
- `presentaciones`: catalogo de formatos como Caja, Bolsa o Sobre.
- `productos`: catalogo principal de productos.
- `inventario_movimientos`: historial de entradas, salidas y ajustes de inventario.

## Roles del sistema
- Admin
- Operador
- Auditor

## Rol: Admin
Permisos:
- Iniciar sesion
- Acceder al menu principal
- Crear usuarios
- Modificar usuarios
- Activar/inactivar usuarios
- Ver listado de usuarios
- Generar reporte de usuarios
- Crear productos
- Modificar productos
- Eliminar productos sin movimientos de inventario
- Registrar movimientos de inventario
- Ver reportes de inventario

## Rol: Operador
Permisos:
- Iniciar sesion
- Acceder al menu principal
- Crear productos
- Modificar productos
- Eliminar productos sin movimientos de inventario
- Registrar movimientos de inventario
- Ver reportes de inventario

## Rol: Auditor
Permisos:
- Iniciar sesion
- Acceder al menu principal
- Ver productos
- Ver reportes de inventario

# PLUGIN O CONECTOR PARA LA DB BRO
sudo apt install python3-mysql.connector, python3 -c "import mysql.connector; print('Conexión MySQL lista')"
py -m pip install mysql-connector-python, python -m pip install mysql-connector-python
