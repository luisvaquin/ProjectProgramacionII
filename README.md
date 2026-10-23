# Proyecto Luis Rodrigo Vaquin

## Ejecutar el sistema

Desde la raíz del proyecto:

```bash
python3 main.py
```

## Estructura MVC

```text
main.py
model/
  conexion.py             conexión a MySQL
  usuarios_model.py       consultas de usuarios y autenticación
  productos_model.py      consultas y registros de productos
  catalogos_model.py      consultas de unidades de medida y presentaciones
controller/
  auth_controller.py      validación de inicio de sesión
  usuarios_controller.py  reglas del CRUD de usuarios
  productos_controller.py reglas del catálogo de productos
view/
  auth/                   login, registro y estilos de autenticación
  main/                   menú principal, dashboard y estilos
arc/                      script SQL y documentación del proyecto
tests/                    pruebas automatizadas
```

### Responsabilidad de cada capa

- `model`: se conecta a MySQL y contiene consultas SQL. No crea ventanas ni muestra mensajes.
- `controller`: valida datos, aplica permisos por rol y llama a los modelos. No escribe SQL ni construye controles Tkinter.
- `view`: contiene ventanas, campos, tablas y botones. Solicita acciones a los controladores y muestra el resultado.

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

## Conector MySQL

En Ubuntu/Debian:

```bash
sudo apt install python3-mysql.connector
```

En Windows:

```bash
py -m pip install mysql-connector-python
```

## Imágenes de productos

El catálogo admite una URL de imagen por producto y la muestra en la vista de tarjetas.
La primera vez que se consulta una imagen, el sistema guarda una copia temporal en
`assets/productos/`; esa carpeta se puede borrar con seguridad porque se vuelve a crear.

Para mostrar imágenes, instale Pillow:

```bash
# Ubuntu/Debian
sudo apt install python3-pil

# Windows
py -m pip install Pillow
```
