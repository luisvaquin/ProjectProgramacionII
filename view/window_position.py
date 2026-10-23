"""Utilidades para posicionar ventanas en el monitor principal."""

import re
import subprocess
import sys


_PANTALLA_PRINCIPAL = re.compile(
    r"^\S+ connected primary (\d+)x(\d+)\+(-?\d+)\+(-?\d+)",
)


def centrar_en_pantalla_principal(ventana, ancho_preferido, alto_preferido, margen=40):
    """Centra una ventana en la pantalla principal, incluso con dos monitores."""
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    origen_x = origen_y = 0

    if sys.platform.startswith("linux"):
        try:
            resultado = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                check=False,
                timeout=1,
            )
            for linea in resultado.stdout.splitlines():
                coincidencia = _PANTALLA_PRINCIPAL.match(linea)
                if coincidencia:
                    ancho_pantalla, alto_pantalla, origen_x, origen_y = map(
                        int, coincidencia.groups(),
                    )
                    break
        except (OSError, subprocess.SubprocessError):
            pass

    ancho = min(ancho_preferido, max(ancho_pantalla - margen * 2, 1))
    alto = min(alto_preferido, max(alto_pantalla - margen * 2, 1))
    x = origen_x + (ancho_pantalla - ancho) // 2
    y = origen_y + (alto_pantalla - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")
