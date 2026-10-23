from decimal import Decimal, InvalidOperation
from model import catalogos_model, productos_model


def obtener_productos():
    try:
        return {"ok": True, "productos": productos_model.listar_productos(), "mensaje": ""}
    except Exception:
        return {
            "ok": False,
            "productos": [],
            "mensaje": "No se pudieron cargar los productos. Revise la conexión con MySQL.",
        }


def obtener_catalogos_producto():
    try:
        return {
            "ok": True,
            "unidades": catalogos_model.listar_unidades_medida(),
            "presentaciones": catalogos_model.listar_presentaciones(),
            "mensaje": "",
        }
    except Exception:
        return {
            "ok": False,
            "unidades": [],
            "presentaciones": [],
            "mensaje": "No se pudieron cargar los catálogos de producto.",
        }


def registrar_producto(id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio):
    codigo, descripcion = codigo.strip().upper(), descripcion.strip()
    imagen_url = imagen_url.strip() or None
    if not codigo or not descripcion or not id_unidad or not id_presentacion or not precio.strip():
        return {"ok": False, "mensaje": "Complete todos los campos."}
    if len(codigo) > 20 or len(descripcion) > 150 or (imagen_url and len(imagen_url) > 500):
        return {"ok": False, "mensaje": "El código admite hasta 20, la descripción 150 y la URL 500 caracteres."}
    try:
        precio_decimal = Decimal(precio)
    except InvalidOperation:
        return {"ok": False, "mensaje": "Ingrese un precio válido."}
    if not precio_decimal.is_finite() or precio_decimal < 0:
        return {"ok": False, "mensaje": "El precio no puede ser negativo."}
    try:
        productos_model.crear_producto(
            id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio_decimal
        )
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception as error:
        if getattr(error, "errno", None) == 1062:
            return {"ok": False, "mensaje": "Ese código de producto ya existe."}
        return {"ok": False, "mensaje": "No se pudo registrar el producto. Revise la conexión con MySQL."}
    return {"ok": True, "mensaje": "Producto registrado correctamente."}


def actualizar_producto(id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio, estado):
    codigo, descripcion = codigo.strip().upper(), descripcion.strip()
    imagen_url = imagen_url.strip() or None
    if not codigo or not descripcion or not id_unidad or not id_presentacion or not precio.strip():
        return {"ok": False, "mensaje": "Complete todos los campos."}
    if len(codigo) > 20 or len(descripcion) > 150 or (imagen_url and len(imagen_url) > 500):
        return {"ok": False, "mensaje": "El código admite hasta 20, la descripción 150 y la URL 500 caracteres."}
    if estado not in ("ACTIVO", "INACTIVO"):
        return {"ok": False, "mensaje": "Seleccione un estado válido."}
    try:
        precio_decimal = Decimal(precio)
    except InvalidOperation:
        return {"ok": False, "mensaje": "Ingrese un precio válido."}
    if not precio_decimal.is_finite() or precio_decimal < 0:
        return {"ok": False, "mensaje": "El precio no puede ser negativo."}
    try:
        productos_model.actualizar_producto(
            id_usuario, codigo, descripcion, imagen_url, id_unidad, id_presentacion, precio_decimal, estado
        )
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception:
        return {"ok": False, "mensaje": "No se pudo actualizar el producto. Revise la conexión con MySQL."}
    return {"ok": True, "mensaje": "Producto actualizado correctamente."}


def eliminar_producto(id_usuario, codigo):
    codigo = codigo.strip().upper()
    if not codigo:
        return {"ok": False, "mensaje": "Seleccione un producto."}
    try:
        productos_model.eliminar_producto(id_usuario, codigo)
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception:
        return {"ok": False, "mensaje": "No se pudo eliminar el producto. Revise la conexión con MySQL."}
    return {"ok": True, "mensaje": "Producto eliminado correctamente."}
