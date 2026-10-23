import tkinter as tk
from tkinter import messagebox

from controller.auth_controller import validar_login
from view.auth.login_styles import CARD, COLORS, FONTS, WINDOW
from view.auth.register import RegisterView
from view.main.main import MainView
from view.window_position import centrar_en_pantalla_principal


class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Control - Login")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.resizable(False, False)
        self.configure(bg=COLORS["window_background"])

        self.usuario_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.mostrar_password_var = tk.BooleanVar(value=False)

        self._centrar_ventana()
        self._crear_vista()
        self.after_idle(self._centrar_ventana)
        self.bind("<Return>", lambda event: self._aceptar())
        self.bind("<Escape>", lambda event: self._cancelar())

    def _centrar_ventana(self):
        centrar_en_pantalla_principal(self, WINDOW["width"], WINDOW["height"])

    def _crear_vista(self):
        contenedor = tk.Frame(
            self,
            bg=COLORS["card_background"],
            padx=CARD["padding_x"],
            pady=CARD["padding_y"],
            relief="flat",
            bd=0,
            highlightthickness=0,
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

        tk.Label(
            contenedor,
            text="SISTEMA DE CONTROL",
            bg=COLORS["card_background"],
            fg=COLORS["primary"],
            font=FONTS["label"],
        ).pack(pady=(0, 10))

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
            relief="flat",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
        usuario_entry.pack(fill="x", ipady=8, pady=(0, 18))
        self.usuario_entry = usuario_entry
        usuario_entry.focus()

        self._crear_label(contenedor, "Contraseña")
        password_entry = tk.Entry(
            contenedor,
            textvariable=self.password_var,
            show="*",
            font=FONTS["input"],
            bg=COLORS["input_background"],
            fg=COLORS["input_text"],
            relief="flat",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
        self.password_entry = password_entry
        password_entry.pack(fill="x", ipady=8, pady=(0, 4))

        tk.Checkbutton(
            contenedor,
            text="Mostrar contraseña",
            variable=self.mostrar_password_var,
            command=self._alternar_password,
            bg=COLORS["card_background"],
            activebackground=COLORS["card_background"],
            fg=COLORS["muted"],
            activeforeground=COLORS["text"],
            font=FONTS["note"],
            selectcolor=COLORS["card_background"],
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 22))

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

        tk.Label(contenedor, text="¿No tienes una cuenta?",
                 bg=COLORS["card_background"], fg=COLORS["muted"],
                 font=FONTS["note"]).pack(pady=(20, 2))
        tk.Button(contenedor, text="Crear cuenta", command=self._abrir_registro,
                  bg=COLORS["card_background"], fg=COLORS["primary"],
                  activebackground=COLORS["card_background"],
                  activeforeground=COLORS["primary_active"],
                  font=FONTS["button"], relief="flat", cursor="hand2").pack()

    def _abrir_registro(self):
        RegisterView(self, al_registrar=self._cuenta_creada)

    def _alternar_password(self):
        self.password_entry.configure(show="" if self.mostrar_password_var.get() else "*")

    def _cuenta_creada(self, usuario):
        self.usuario_var.set(usuario)
        self.password_var.set("")
        self.password_entry.focus_set()

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
        self.password_var.set("")
        self.mostrar_password_var.set(False)
        self._alternar_password()
        self._abrir_menu_principal(usuario_encontrado)

    def _abrir_menu_principal(self, usuario):
        self.withdraw()
        MainView(self, usuario, self._volver_al_login)

    def _volver_al_login(self):
        self.deiconify()
        self.password_var.set("")
        self.usuario_entry.focus_set()

    def _cancelar(self):
        self.usuario_var.set("")
        self.password_var.set("")
        self.mostrar_password_var.set(False)
        self._alternar_password()
        self.focus_force()


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()
