import tkinter as tk
from tkinter import messagebox, ttk

from controller import usuarios_controller
from view.auth import register_styles as styles


class RegisterView(tk.Toplevel):
    def __init__(self, master, administrador=None, al_registrar=None):
        super().__init__(master)
        self.id_administrador = administrador["id_usuario"] if administrador else None
        self.al_registrar = al_registrar
        self.title("Registrar usuario")
        self.geometry(f"{styles.WINDOW['width']}x{styles.WINDOW['height']}")
        self.resizable(False, False)
        self.configure(bg=styles.COLORS["window_background"])
        self.transient(master)
        self.grab_set()
        self._centrar_sobre_master(master)
        self.variables = {}
        panel = tk.Frame(
            self,
            bg=styles.COLORS["card_background"],
            padx=32,
            pady=24,
            relief="flat",
            bd=0,
            highlightbackground=styles.COLORS["border"],
            highlightthickness=1,
        )
        panel.pack(fill="both", expand=True, padx=20, pady=20)
        titulo = "Registrar usuario" if self.id_administrador is not None else "Crear cuenta"
        subtitulo = "Complete la información para continuar."
        tk.Label(panel, text=titulo, font=styles.FONTS["title"],
                 bg=styles.COLORS["card_background"], fg=styles.COLORS["title"]).pack(pady=(0, 18))
        tk.Label(panel, text=subtitulo, font=styles.FONTS["subtitle"],
                 bg=styles.COLORS["card_background"], fg=styles.COLORS["muted"]).pack(pady=(0, 10))
        for clave, titulo in (("nombre", "Nombre completo"), ("usuario", "Usuario"),
                              ("password", "Contraseña (mínimo 8 caracteres)"),
                              ("confirmacion", "Confirmar contraseña")):
            tk.Label(panel, text=titulo, anchor="w", bg=styles.COLORS["card_background"],
                     font=styles.FONTS["label"]).pack(fill="x", pady=(8, 4))
            variable = tk.StringVar(self)
            self.variables[clave] = variable
            entrada = tk.Entry(panel, textvariable=variable, font=styles.FONTS["input"],
                               show="*" if clave in ("password", "confirmacion") else "",
                               bg=styles.COLORS["input_background"],
                               fg=styles.COLORS["input_text"],
                               relief="flat", bd=0,
                               highlightbackground=styles.COLORS["border"],
                               highlightcolor=styles.COLORS["primary"])
            entrada.pack(fill="x", ipady=6)
            if clave == "nombre":
                self.nombre_entry = entrada
        self.roles = {}
        if self.id_administrador is not None:
            tk.Label(panel, text="Rol", anchor="w", bg=styles.COLORS["card_background"],
                     font=styles.FONTS["label"]).pack(fill="x", pady=(12, 4))
            self.rol = ttk.Combobox(panel, state="readonly", font=styles.FONTS["input"])
            self.rol.pack(fill="x", ipady=4)
        else:
            tk.Label(panel, text="Tu cuenta tendrá el rol Operador.",
                     bg=styles.COLORS["card_background"], fg=styles.COLORS["muted"],
                     font=styles.FONTS["note"]).pack(pady=(12, 0))
        self.guardar = tk.Button(panel, text="REGISTRAR", command=self._registrar,
                                bg=styles.COLORS["primary"], fg="white", font=styles.FONTS["button"],
                                activebackground=styles.COLORS["primary_active"],
                                activeforeground="white", relief="flat", cursor="hand2")
        self.guardar.pack(fill="x", ipady=8, pady=(22, 8))
        tk.Button(panel, text="CERRAR", command=self.destroy,
                  bg=styles.COLORS["secondary"], fg=styles.COLORS["secondary_text"],
                  activebackground=styles.COLORS["secondary_active"],
                  activeforeground=styles.COLORS["secondary_text_active"],
                  font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", ipady=6)
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: self._registrar())
        if self.id_administrador is not None:
            self.after_idle(self._cargar_roles)
        else:
            self.after_idle(self.nombre_entry.focus_set)

    def _centrar_sobre_master(self, master):
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _cargar_roles(self):
        respuesta = usuarios_controller.obtener_roles()
        self.roles = {r["nombre"]: r["id_rol"] for r in respuesta["roles"]}
        self.rol.configure(values=list(self.roles))
        if not respuesta["ok"]:
            self.guardar.configure(state="disabled")
            messagebox.showerror("Roles no disponibles", respuesta["mensaje"], parent=self)
        self.nombre_entry.focus_set()

    def _registrar(self):
        self.guardar.configure(state="disabled")
        try:
            datos = [self.variables[c].get() for c in
                     ("nombre", "usuario", "password", "confirmacion")]
            if self.id_administrador is None:
                respuesta = usuarios_controller.registrar_cuenta(*datos)
            else:
                respuesta = usuarios_controller.registrar_usuario(
                    self.id_administrador, *datos, self.roles.get(self.rol.get()))
            if not respuesta["ok"]:
                messagebox.showerror("Registro", respuesta["mensaje"], parent=self)
                return
            messagebox.showinfo("Registro", respuesta["mensaje"], parent=self)
            if self.id_administrador is None:
                if self.al_registrar:
                    self.al_registrar(self.variables["usuario"].get().strip())
                self.destroy()
                return
            for variable in self.variables.values():
                variable.set("")
            self.rol.set("")
            self.nombre_entry.focus_set()
        finally:
            if self.winfo_exists():
                self.guardar.configure(state="normal")


if __name__ == "__main__":
    from view.auth.login import LoginView

    LoginView().mainloop()
