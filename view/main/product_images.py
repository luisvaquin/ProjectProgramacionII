"""Carga y conserva localmente las imágenes remotas del catálogo."""

from base64 import b64encode
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError
import tkinter as tk


_CACHE_DIR = Path(__file__).resolve().parents[2] / "assets" / "productos"
_MAX_BYTES = 3 * 1024 * 1024


def obtener_imagen_producto(url, ancho=230, alto=122):
    """Devuelve una PhotoImage ajustada o None cuando no se puede cargar."""
    if not url:
        return None

    ruta_cache = _CACHE_DIR / f"{sha256(url.encode('utf-8')).hexdigest()}.img"
    try:
        if ruta_cache.exists():
            contenido = ruta_cache.read_bytes()
        else:
            solicitud = Request(url, headers={"User-Agent": "ERP-Luisvaquin/1.0"})
            with urlopen(solicitud, timeout=8) as respuesta:
                contenido = respuesta.read(_MAX_BYTES + 1)
            if not contenido or len(contenido) > _MAX_BYTES:
                return None
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            ruta_cache.write_bytes(contenido)

        with Image.open(BytesIO(contenido)) as original:
            imagen_ajustada = ImageOps.contain(
                original.convert("RGB"),
                (ancho, alto),
                method=Image.Resampling.LANCZOS,
            )
        imagen = Image.new("RGB", (ancho, alto), "#f8fafc")
        posicion_x = (ancho - imagen_ajustada.width) // 2
        posicion_y = (alto - imagen_ajustada.height) // 2
        imagen.paste(imagen_ajustada, (posicion_x, posicion_y))
        salida = BytesIO()
        imagen.save(salida, format="PNG")
        return tk.PhotoImage(data=b64encode(salida.getvalue()))
    except (OSError, UnidentifiedImageError, ValueError):
        return None
