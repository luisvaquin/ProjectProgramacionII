from datetime import datetime

from model import inventario_model


TIPOS_MOVIMIENTO = ("ENTRADA", "SALIDA", "AJUSTE")
DIRECCIONES_AJUSTE = ("SUMA", "RESTA")


def obtener_productos_inventario():
    try:
        return {
            "ok": True,
            "productos": inventario_model.listar_productos_inventario(),
            "mensaje": "",
        }
    except Exception:
        return {
            "ok": False,
            "productos": [],
            "mensaje": "No se pudieron cargar los productos de inventario.",
        }


def obtener_movimientos():
    try:
        return {
            "ok": True,
            "movimientos": inventario_model.listar_movimientos(),
            "mensaje": "",
        }
    except Exception:
        return {
            "ok": False,
            "movimientos": [],
            "mensaje": "No se pudo cargar el historial de movimientos.",
        }


def obtener_resumen_dashboard():
    try:
        return {
            "ok": True,
            "resumen": inventario_model.obtener_resumen_dashboard(),
            "actividad": inventario_model.listar_actividad_reciente(),
            "mensaje": "",
        }
    except Exception:
        return {
            "ok": False,
            "resumen": {
                "productos_activos": "--",
                "existencia_total": "--",
                "movimientos_recientes": "--",
            },
            "actividad": [],
            "mensaje": "No se pudo cargar el resumen de inventario.",
        }


def obtener_reporte_inventario(codigo="", descripcion="", fecha=""):
    codigo = codigo.strip().upper()
    descripcion = descripcion.strip()
    fecha = fecha.strip()
    if len(codigo) > 20 or len(descripcion) > 150:
        return {
            "ok": False,
            "registros": [],
            "mensaje": "El código admite hasta 20 caracteres y la descripción hasta 150.",
        }
    if fecha:
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return {
                "ok": False,
                "registros": [],
                "mensaje": "Ingrese la fecha en formato AAAA-MM-DD.",
            }
    try:
        registros = inventario_model.listar_reporte_inventario(
            codigo or None, descripcion or None, fecha or None
        )
        return {"ok": True, "registros": registros, "mensaje": ""}
    except Exception:
        return {
            "ok": False,
            "registros": [],
            "mensaje": "No se pudo generar el reporte de inventario.",
        }
def registrar_movimiento(id_usuario, codigo_producto, tipo_movimiento, cantidad,
                         observacion, direccion_ajuste=None):
    codigo_producto = codigo_producto.strip().upper()
    tipo_movimiento = tipo_movimiento.strip().upper()
    direccion_ajuste = (direccion_ajuste or "").strip().upper() or None
    observacion = observacion.strip()

    if not codigo_producto or tipo_movimiento not in TIPOS_MOVIMIENTO:
        return {"ok": False, "mensaje": "Seleccione un producto y tipo de movimiento válidos."}
    try:
        cantidad_entera = int(cantidad)
    except (TypeError, ValueError):
        return {"ok": False, "mensaje": "La cantidad debe ser un número entero."}
    if cantidad_entera <= 0:
        return {"ok": False, "mensaje": "La cantidad debe ser mayor que cero."}
    if len(observacion) > 200:
        return {"ok": False, "mensaje": "La observación admite hasta 200 caracteres."}
    if tipo_movimiento == "AJUSTE" and direccion_ajuste not in DIRECCIONES_AJUSTE:
        return {"ok": False, "mensaje": "Indique si el ajuste suma o resta existencia."}
    if tipo_movimiento != "AJUSTE":
        direccion_ajuste = None

    try:
        inventario_model.registrar_movimiento(
            id_usuario, codigo_producto, tipo_movimiento, cantidad_entera,
            observacion, direccion_ajuste,
        )
    except (PermissionError, ValueError) as error:
        return {"ok": False, "mensaje": str(error)}
    except Exception:
        return {"ok": False, "mensaje": "No se pudo registrar el movimiento. Revise la conexión con MySQL."}

    if tipo_movimiento == "AJUSTE":
        nombre_movimiento = f"Ajuste de inventario ({direccion_ajuste.lower()})"
    elif tipo_movimiento == "ENTRADA":
        nombre_movimiento = "Entrada por reabastecimiento"
    else:
        nombre_movimiento = "Salida registrada"
    return {"ok": True, "mensaje": f"{nombre_movimiento} correctamente."}
