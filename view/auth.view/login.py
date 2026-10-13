from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import sys
import tkinter as tk
from tkinter import messagebox

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGIN_STYLES_PATH = Path(__file__).resolve().with_name("login.styles.py")
LOGIN_CONTROLLER_PATH = (
    PROJECT_ROOT / "controller" / "auth.controller" / "login.controller.py"
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _cargar_modulo(nombre, ruta):
    spec = spec_from_file_location(nombre, ruta)
    modulo = module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


login_styles = _cargar_modulo("login_styles", LOGIN_STYLES_PATH)
login_controller = _cargar_modulo("login_controller", LOGIN_CONTROLLER_PATH)

CARD = login_styles.CARD
COLORS = login_styles.COLORS
FONTS = login_styles.FONTS
WINDOW = login_styles.WINDOW
validar_login = login_controller.validar_login


class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Control - Login")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.resizable(False, False)
        self.configure(bg=COLORS["window_background"])

        self.usuario_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._centrar_ventana()
        self._crear_vista()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = WINDOW["width"]
        alto = WINDOW["height"]
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_vista(self):
        contenedor = tk.Frame(
            self,
            bg=COLORS["card_background"],
            padx=CARD["padding_x"],
            pady=CARD["padding_y"],
        )
        contenedor.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=CARD["width"],
            height=CARD["height"],
        )

        titulo = tk.Label(
            contenedor,
            text="EMPRESA UMG",
            bg=COLORS["card_background"],
            fg=COLORS["title"],
            font=FONTS["title"],
        )
        titulo.pack(pady=(0, 8))

        subtitulo = tk.Label(
            contenedor,
            text="Ingreso al sistema",
            bg=COLORS["card_background"],
            fg=COLORS["muted"],
            font=FONTS["subtitle"],
        )
        subtitulo.pack(pady=(0, 28))

        self._crear_label(contenedor, "Usuario")
        usuario_entry = tk.Entry(
            contenedor,
            textvariable=self.usuario_var,
            font=FONTS["input"],
            bg=COLORS["input_background"],
            fg=COLORS["input_text"],
            relief="solid",
            bd=1,
        )
        usuario_entry.pack(fill="x", ipady=8, pady=(0, 18))
        usuario_entry.focus()

        self._crear_label(contenedor, "Contraseña")
        password_entry = tk.Entry(
            contenedor,
            textvariable=self.password_var,
            show="*",
            font=FONTS["input"],
            bg=COLORS["input_background"],
            fg=COLORS["input_text"],
            relief="solid",
            bd=1,
        )
        password_entry.pack(fill="x", ipady=8, pady=(0, 26))

        boton_aceptar = tk.Button(
            contenedor,
            text="ACEPTAR",
            command=self._aceptar,
            bg=COLORS["primary"],
            fg=COLORS["button_text"],
            activebackground=COLORS["primary_active"],
            activeforeground=COLORS["button_text"],
            font=FONTS["button"],
            relief="flat",
            cursor="hand2",
        )
        boton_aceptar.pack(fill="x", ipady=9, pady=(0, 12))

        boton_cancelar = tk.Button(
            contenedor,
            text="CANCELAR",
            command=self._cancelar,
            bg=COLORS["secondary"],
            fg=COLORS["secondary_text"],
            activebackground=COLORS["secondary_active"],
            activeforeground=COLORS["secondary_text_active"],
            font=FONTS["button"],
            relief="flat",
            cursor="hand2",
        )
        boton_cancelar.pack(fill="x", ipady=9)

        nota = tk.Label(
            contenedor,
            text="Validación conectada a MySQL",
            bg=COLORS["card_background"],
            fg=COLORS["note"],
            font=FONTS["note"],
        )
        nota.pack(side="bottom", pady=(18, 0))

    def _crear_label(self, contenedor, texto):
        label = tk.Label(
            contenedor,
            text=texto,
            bg=COLORS["card_background"],
            fg=COLORS["text"],
            font=FONTS["label"],
            anchor="w",
        )
        label.pack(fill="x", pady=(0, 6))

    def _aceptar(self):
        usuario = self.usuario_var.get()
        password = self.password_var.get()
        respuesta = validar_login(usuario, password)

        if not respuesta["ok"]:
            messagebox.showerror("Acceso denegado", respuesta["mensaje"])
            return

        usuario_encontrado = respuesta["usuario"]
        messagebox.showinfo(
            "Bienvenido",
            f"Hola {usuario_encontrado['nombre_completo']} ({usuario_encontrado['rol']})",
        )

    def _cancelar(self):
        self.usuario_var.set("")
        self.password_var.set("")


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()
