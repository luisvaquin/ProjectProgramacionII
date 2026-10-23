# Arquitectura MVC del proyecto

## Modelo

El modelo trabaja con MySQL. Cada archivo representa una parte de los datos:

- `conexion.py`: abre la conexión a la base de datos.
- `usuarios_model.py`: login, roles, creación, actualización e inactivación de usuarios.
- `productos_model.py`: listado, creación, actualización y eliminación física de productos sin movimientos de inventario.
- `catalogos_model.py`: unidades de medida y presentaciones utilizadas por productos.
- `inventario_model.py`: existencias calculadas, historial, reportería y registro de entradas, salidas y ajustes.

El modelo no debe contener botones, ventanas ni mensajes de Tkinter.

## Controlador

El controlador recibe información desde las vistas, valida las reglas y llama al modelo:

- `auth_controller.py`: valida usuario y contraseña para iniciar sesión.
- `usuarios_controller.py`: controla el CRUD de usuarios y permisos de Admin.
- `productos_controller.py`: valida códigos, precios y permisos para gestionar productos.
- `inventario_controller.py`: valida cantidades, existencia disponible, filtros y permisos para movimientos.

El controlador no debe construir interfaces ni escribir consultas SQL directamente.

## Vista

La vista contiene solo la interfaz:

- `view/auth/`: login y registro de cuenta.
- `view/main/`: dashboard, menú lateral, gestión de usuarios, productos, movimientos y reportes.

La vista captura datos de los formularios, llama al controlador y muestra los resultados.

## Flujo de ejemplo

```text
Vista de Productos
  -> productos_controller.registrar_producto(...)
  -> productos_model.crear_producto(...)
  -> MySQL: tabla productos
  -> respuesta a la vista
```

El módulo de inventario ya sigue esta misma separación MVC para movimientos y reportería.
