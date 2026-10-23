import tkinter as tk
from calendar import monthrange
from datetime import date, datetime
from tkinter import messagebox, ttk

from controller import inventario_controller, productos_controller, usuarios_controller
from view.auth.register import RegisterView
from view.main.product_images import obtener_imagen_producto
from view.main import main_styles as styles
from view.window_position import centrar_en_pantalla_principal


MESES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)


class CalendarioFecha(tk.Toplevel):
    """Selector de fecha sin dependencias externas para los filtros del sistema."""

    def __init__(self, master, variable_fecha):
        super().__init__(master)
        self.variable_fecha = variable_fecha
        self.title("Seleccionar fecha")
        self.resizable(False, False)
        self.configure(bg=styles.COLORS["background"])
        self.transient(master)
        self.grab_set()

        try:
            seleccionada = datetime.strptime(variable_fecha.get(), "%Y-%m-%d").date()
        except ValueError:
            seleccionada = date.today()
        self.anio = seleccionada.year
        self.mes = seleccionada.month
        self._crear_vista()
        self._centrar(master)

    def _centrar(self, master):
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _crear_vista(self):
        self.panel = tk.Frame(
            self,
            bg=styles.COLORS["surface"],
            padx=18,
            pady=16,
            relief="flat",
            bd=0,
            highlightbackground=styles.COLORS["border"],
            highlightthickness=1,
        )
        self.panel.pack(fill="both", expand=True, padx=12, pady=12)
        self._mostrar_mes()

    def _mostrar_mes(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        cabecera = tk.Frame(self.panel, bg=styles.COLORS["surface"])
        cabecera.pack(fill="x", pady=(0, 12))
        tk.Button(
            cabecera, text="<", command=self._mes_anterior,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"], relief="flat", bd=0,
            cursor="hand2", width=3,
        ).pack(side="left")
        tk.Label(
            cabecera, text=f"{MESES[self.mes - 1]} {self.anio}",
            bg=styles.COLORS["surface"], fg=styles.COLORS["title"],
            font=styles.FONTS["card_title"],
        ).pack(side="left", expand=True)
        tk.Button(
            cabecera, text=">", command=self._mes_siguiente,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"], relief="flat", bd=0,
            cursor="hand2", width=3,
        ).pack(side="right")

        dias = tk.Frame(self.panel, bg=styles.COLORS["surface"])
        dias.pack()
        for columna, nombre in enumerate(("L", "M", "X", "J", "V", "S", "D")):
            tk.Label(
                dias, text=nombre, width=4, bg=styles.COLORS["surface"],
                fg=styles.COLORS["muted"], font=styles.FONTS["button"],
            ).grid(row=0, column=columna, pady=(0, 5))

        inicio, total_dias = monthrange(self.anio, self.mes)
        fila, columna = 1, inicio
        for dia in range(1, total_dias + 1):
            fecha_actual = date(self.anio, self.mes, dia)
            es_hoy = fecha_actual == date.today()
            boton = tk.Button(
                dias,
                text=str(dia),
                command=lambda valor=fecha_actual: self._seleccionar(valor),
                width=4,
                bg=styles.COLORS["primary"] if es_hoy else styles.COLORS["secondary"],
                fg=styles.COLORS["button_text"] if es_hoy else styles.COLORS["text"],
                activebackground=styles.COLORS["primary_active"],
                activeforeground=styles.COLORS["button_text"],
                relief="flat",
                bd=0,
                cursor="hand2",
            )
            boton.grid(row=fila, column=columna, padx=2, pady=2)
            columna += 1
            if columna == 7:
                columna = 0
                fila += 1

        acciones = tk.Frame(self.panel, bg=styles.COLORS["surface"])
        acciones.pack(fill="x", pady=(12, 0))
        tk.Button(
            acciones, text="HOY", command=lambda: self._seleccionar(date.today()),
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"], relief="flat", bd=0,
            cursor="hand2", font=styles.FONTS["button"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=5)
        tk.Button(
            acciones, text="CANCELAR", command=self.destroy,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"], relief="flat", bd=0,
            cursor="hand2", font=styles.FONTS["button"],
        ).pack(side="left", fill="x", expand=True, padx=(4, 0), ipady=5)

    def _mes_anterior(self):
        self.mes -= 1
        if self.mes == 0:
            self.mes, self.anio = 12, self.anio - 1
        self._mostrar_mes()

    def _mes_siguiente(self):
        self.mes += 1
        if self.mes == 13:
            self.mes, self.anio = 1, self.anio + 1
        self._mostrar_mes()

    def _seleccionar(self, fecha):
        self.variable_fecha.set(fecha.isoformat())
        self.destroy()


class MainView(tk.Toplevel):
    def __init__(self, master, usuario, al_cerrar_sesion):
        super().__init__(master)
        self.usuario = usuario
        self.al_cerrar_sesion = al_cerrar_sesion
        self.rol = usuario["rol"].upper()

        self.title("Sistema de Control - Menú principal")
        self.geometry(f"{styles.WINDOW['width']}x{styles.WINDOW['height']}")
        self.minsize(980, 620)
        self.configure(bg=styles.COLORS["background"])
        self.protocol("WM_DELETE_WINDOW", self._cerrar_sesion)

        self._centrar_ventana()
        self._configurar_estilos()
        self._crear_vista()
        self.after_idle(self._centrar_ventana)
        self.lift()
        self.focus_force()

    def _centrar_ventana(self):
        centrar_en_pantalla_principal(
            self, styles.WINDOW["width"], styles.WINDOW["height"],
        )

    @staticmethod
    def _permitir_entero(valor):
        return not valor or valor.isdigit()

    @staticmethod
    def _permitir_precio(valor):
        if not valor:
            return True
        if valor.count(".") > 1:
            return False
        entero, separador, decimal = valor.partition(".")
        return entero.isdigit() and (
            not separador or (len(decimal) <= 2 and (not decimal or decimal.isdigit()))
        )

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        self.option_add("*Entry.background", styles.COLORS["input"])
        self.option_add("*Entry.foreground", styles.COLORS["text"])
        self.option_add("*Entry.relief", "flat")
        self.option_add("*Entry.borderWidth", 0)
        self.option_add("*Entry.highlightThickness", 1)
        self.option_add("*Entry.highlightBackground", styles.COLORS["border"])
        self.option_add("*Entry.highlightColor", styles.COLORS["primary"])
        self.option_add("*Entry.insertBackground", styles.COLORS["title"])
        estilo.configure(
            "Treeview",
            background=styles.COLORS["table"],
            fieldbackground=styles.COLORS["table"],
            foreground=styles.COLORS["text"],
            rowheight=30,
            borderwidth=0,
            font=styles.FONTS["card_text"],
        )
        estilo.map(
            "Treeview",
            background=[("selected", styles.COLORS["primary"])],
            foreground=[("selected", styles.COLORS["button_text"])],
        )
        estilo.configure(
            "Treeview.Heading",
            background="#dfe6ef",
            foreground=styles.COLORS["title"],
            font=styles.FONTS["button"],
            relief="flat",
            padding=(8, 7),
        )
        estilo.map("Treeview.Heading", background=[("active", "#d2dce9")])
        estilo.configure(
            "TCombobox",
            padding=6,
            fieldbackground=styles.COLORS["input"],
            background=styles.COLORS["secondary"],
            foreground=styles.COLORS["text"],
            bordercolor=styles.COLORS["border"],
            lightcolor=styles.COLORS["border"],
            darkcolor=styles.COLORS["border"],
        )

    def _crear_panel(self, master, padx=18, pady=18):
        return tk.Frame(
            master,
            bg=styles.COLORS["surface"],
            padx=padx,
            pady=pady,
            relief="flat",
            bd=0,
            highlightbackground=styles.COLORS["border"],
            highlightthickness=1,
        )

    def _crear_vista(self):
        lateral = tk.Frame(self, bg=styles.COLORS["sidebar"], width=232)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.botones_menu = {}

        tk.Label(
            lateral,
            text="EMPRESA UMG",
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            font=styles.FONTS["brand"],
        ).pack(anchor="w", padx=24, pady=(34, 8))
        tk.Label(
            lateral,
            text="Sistema de control",
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            font=styles.FONTS["subtitle"],
        ).pack(anchor="w", padx=24)

        tk.Frame(
            lateral, height=1, bg=styles.COLORS["sidebar_separator"],
        ).pack(fill="x", padx=20, pady=(28, 16))
        self._agregar_opcion_menu(lateral, "Inicio", self._mostrar_inicio)

        if self.rol == "ADMIN":
            self._agregar_opcion_menu(lateral, "Usuarios", self._mostrar_usuarios)

        self._agregar_opcion_menu(lateral, "Productos", self._mostrar_productos)

        if self.rol in ("ADMIN", "OPERADOR"):
            self._agregar_opcion_menu(lateral, "Movimientos", self._mostrar_movimientos)

        self._agregar_opcion_menu(lateral, "Inventario-Reportes", self._mostrar_reportes)

        tk.Frame(
            lateral, height=1, bg=styles.COLORS["sidebar_separator"],
        ).pack(fill="x", padx=20, pady=(20, 20))
        tk.Label(
            lateral,
            text="Sesión activa",
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            font=styles.FONTS["subtitle"],
        ).pack(anchor="w", padx=24)
        tk.Label(
            lateral,
            text=self.usuario["nombre_completo"],
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            font=styles.FONTS["user"],
            wraplength=170,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(5, 2))
        tk.Label(
            lateral,
            text=f"Rol: {self.usuario['rol']}",
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            font=styles.FONTS["subtitle"],
        ).pack(anchor="w", padx=24)

        tk.Button(
            lateral,
            text="CERRAR SESIÓN",
            command=self._cerrar_sesion,
            bg=styles.COLORS["neutral"],
            fg=styles.COLORS["button_text"],
            activebackground=styles.COLORS["neutral_active"],
            activeforeground=styles.COLORS["button_text"],
            font=styles.FONTS["button"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        ).pack(side="bottom", fill="x", padx=24, pady=28, ipady=8)

        self.contenido = tk.Frame(self, bg=styles.COLORS["background"], padx=38, pady=34)
        self.contenido.pack(side="left", fill="both", expand=True)
        self._mostrar_inicio()

    def _agregar_opcion_menu(self, master, nombre, accion):
        boton = tk.Button(
            master,
            text=nombre,
            command=accion,
            anchor="w",
            padx=24,
            pady=10,
            bg=styles.COLORS["sidebar"],
            fg=styles.COLORS["sidebar_text"],
            activebackground=styles.COLORS["sidebar_active"],
            activeforeground=styles.COLORS["sidebar_text"],
            font=styles.FONTS["button"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        boton.pack(fill="x")
        self.botones_menu[nombre] = boton

    def _limpiar_contenido(self, opcion):
        for widget in self.contenido.winfo_children():
            widget.destroy()
        for nombre, boton in self.botones_menu.items():
            boton.configure(bg=styles.COLORS["sidebar_active"] if nombre == opcion else styles.COLORS["sidebar"])

    def _encabezado(self, titulo, descripcion):
        tk.Label(
            self.contenido,
            text=titulo,
            bg=styles.COLORS["background"],
            fg=styles.COLORS["title"],
            font=styles.FONTS["title"],
        ).pack(anchor="w")
        tk.Label(
            self.contenido,
            text=descripcion,
            bg=styles.COLORS["background"],
            fg=styles.COLORS["muted"],
            font=styles.FONTS["subtitle"],
        ).pack(anchor="w", pady=(6, 26))

    def _mostrar_inicio(self):
        self._limpiar_contenido("Inicio")
        self._encabezado(
            f"Bienvenido, {self.usuario['nombre_completo']}",
            "Resumen general del sistema de control.",
        )
        acciones = tk.Frame(self.contenido, bg=styles.COLORS["background"])
        acciones.pack(fill="x", pady=(0, 14))
        tk.Button(
            acciones,
            text="ACTUALIZAR RESUMEN",
            command=self._mostrar_inicio,
            bg=styles.COLORS["secondary"],
            fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"],
            activeforeground=styles.COLORS["title"],
            font=styles.FONTS["button"],
            relief="flat",
            cursor="hand2",
        ).pack(side="right", ipady=7, ipadx=12)
        respuesta = inventario_controller.obtener_resumen_dashboard()
        resumen_datos = respuesta["resumen"]
        resumen = tk.Frame(self.contenido, bg=styles.COLORS["background"])
        resumen.pack(fill="x")
        resumen.columnconfigure((0, 1, 2), weight=1, uniform="resumen")
        for columna, (titulo, valor, detalle) in enumerate((
            ("Productos activos", resumen_datos["productos_activos"], "Catálogo disponible"),
            ("Existencia total", resumen_datos["existencia_total"], "Unidades en inventario"),
            ("Movimientos recientes", resumen_datos["movimientos_recientes"], "Últimos 7 días"),
        )):
            tarjeta = self._crear_panel(resumen, padx=18, pady=18)
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=(0, 14) if columna < 2 else 0)
            tk.Label(tarjeta, text=titulo, bg=styles.COLORS["surface"], fg=styles.COLORS["muted"], font=styles.FONTS["card_text"]).pack(anchor="w")
            tk.Label(tarjeta, text=valor, bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["title"]).pack(anchor="w", pady=(8, 0))
            tk.Label(tarjeta, text=detalle, bg=styles.COLORS["surface"], fg=styles.COLORS["muted"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(3, 0))

        actividad = self._crear_panel(self.contenido, padx=22, pady=20)
        actividad.pack(fill="both", expand=True, pady=(22, 0))
        tk.Label(actividad, text="Actividad reciente", bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["card_title"]).pack(anchor="w")
        if not respuesta["ok"]:
            tk.Label(actividad, text=respuesta["mensaje"], bg=styles.COLORS["surface"], fg=styles.COLORS["danger"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(16, 0))
            return
        if not respuesta["actividad"]:
            tk.Label(actividad, text="Aún no hay movimientos registrados en el inventario.", bg=styles.COLORS["surface"], fg=styles.COLORS["muted"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(16, 0))
            return

        columnas = ("fecha", "producto", "movimiento", "cantidad")
        tabla = ttk.Treeview(actividad, columns=columnas, show="headings", height=5)
        encabezados = {
            "fecha": ("Fecha", 105), "producto": ("Producto", 260),
            "movimiento": ("Movimiento", 160), "cantidad": ("Cantidad", 90),
        }
        for columna in columnas:
            titulo, ancho = encabezados[columna]
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="w")
        for movimiento in respuesta["actividad"]:
            tipo = movimiento["tipo_movimiento"].title()
            if movimiento["tipo_movimiento"] == "SALIDA":
                tipo = "Salida por venta"
            elif movimiento["tipo_movimiento"] == "AJUSTE":
                tipo = f"Ajuste ({movimiento['direccion_ajuste'].lower()})"
            tabla.insert("", "end", values=(
                movimiento["fecha"].strftime("%d/%m/%Y"),
                f"{movimiento['codigo_producto']} - {movimiento['descripcion']}",
                tipo, movimiento["cantidad"],
            ))
        tabla.pack(fill="both", expand=True, pady=(14, 0))

    def _mostrar_modulo(self, nombre, descripcion):
        self._limpiar_contenido(nombre)
        self._encabezado(nombre, descripcion)
        panel = self._crear_panel(self.contenido, padx=24, pady=24)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Sin registros para mostrar", bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["card_title"]).pack(anchor="w")
        tk.Label(panel, text="La estructura de esta vista está lista. Mostraremos aquí los datos cuando construyamos este módulo.", bg=styles.COLORS["surface"], fg=styles.COLORS["muted"], font=styles.FONTS["card_text"], justify="left", wraplength=540).pack(anchor="w", pady=(10, 0))

    def _mostrar_usuarios(self):
        self._limpiar_contenido("Usuarios")
        self._encabezado("Usuarios", "Administración de las cuentas del sistema.")

        acciones = tk.Frame(self.contenido, bg=styles.COLORS["background"])
        acciones.pack(fill="x", pady=(0, 16))
        tk.Button(acciones, text="REGISTRAR USUARIO", command=self._abrir_usuarios,
                  bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"],
                  activebackground=styles.COLORS["primary_active"],
                  activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"],
                  relief="flat", cursor="hand2").pack(side="left", ipady=8, ipadx=12)
        tk.Button(acciones, text="ACTUALIZAR", command=self._mostrar_usuarios,
                  bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
                  activebackground=styles.COLORS["secondary_active"],
                  activeforeground=styles.COLORS["title"], font=styles.FONTS["button"],
                  relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)
        tk.Button(acciones, text="EDITAR SELECCIONADO", command=self._abrir_edicion_usuario,
                  bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
                  activebackground=styles.COLORS["secondary_active"],
                  activeforeground=styles.COLORS["title"], font=styles.FONTS["button"],
                  relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)
        tk.Button(acciones, text="INACTIVAR", command=self._inactivar_usuario,
                  bg=styles.COLORS["danger"], fg=styles.COLORS["button_text"],
                  activebackground=styles.COLORS["danger_active"],
                  activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"],
                  relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)

        respuesta = usuarios_controller.obtener_usuarios()
        if not respuesta["ok"]:
            tk.Label(self.contenido, text=respuesta["mensaje"], bg=styles.COLORS["background"],
                     fg=styles.COLORS["danger"], font=styles.FONTS["card_text"]).pack(anchor="w")
            return

        panel = self._crear_panel(self.contenido, padx=12, pady=12)
        panel.pack(fill="both", expand=True)
        columnas = ("id", "nombre", "usuario", "rol", "estado", "registro")
        tabla = ttk.Treeview(panel, columns=columnas, show="headings", selectmode="browse")
        encabezados = {
            "id": ("ID", 50),
            "nombre": ("Nombre completo", 210),
            "usuario": ("Usuario", 120),
            "rol": ("Rol", 100),
            "estado": ("Estado", 90),
            "registro": ("Fecha de registro", 145),
        }
        for columna in columnas:
            titulo, ancho = encabezados[columna]
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="w")

        self.usuarios_por_id = {usuario["id_usuario"]: usuario for usuario in respuesta["usuarios"]}
        for usuario in respuesta["usuarios"]:
            fecha = usuario["fecha_creacion"].strftime("%d/%m/%Y %H:%M")
            tabla.insert("", "end", values=(
                usuario["id_usuario"],
                usuario["nombre_completo"],
                usuario["usuario"],
                usuario["rol"],
                usuario["estado"],
                fecha,
            ))

        desplazamiento = ttk.Scrollbar(panel, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=desplazamiento.set)
        tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")
        self.tabla_usuarios = tabla

    def _usuario_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Usuarios", "Seleccione un usuario de la tabla.", parent=self)
            return None
        valores = self.tabla_usuarios.item(seleccion[0], "values")
        return self.usuarios_por_id.get(int(valores[0]))

    def _abrir_edicion_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario is None:
            return
        respuesta_roles = usuarios_controller.obtener_roles()
        if not respuesta_roles["ok"]:
            messagebox.showerror("Usuarios", respuesta_roles["mensaje"], parent=self)
            return

        roles = {rol["nombre"]: rol["id_rol"] for rol in respuesta_roles["roles"]}
        editor = tk.Toplevel(self)
        editor.title("Editar usuario")
        editor.geometry("460x500")
        editor.resizable(False, False)
        editor.configure(bg=styles.COLORS["background"])
        editor.transient(self)
        editor.grab_set()

        panel = self._crear_panel(editor, padx=28, pady=24)
        panel.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(panel, text="Editar usuario", bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["card_title"]).pack(anchor="w", pady=(0, 14))

        nombre_var = tk.StringVar(value=usuario["nombre_completo"])
        usuario_var = tk.StringVar(value=usuario["usuario"])
        rol_var = tk.StringVar(value=usuario["rol"])
        estado_var = tk.StringVar(value=usuario["estado"])

        for texto, variable in (("Nombre completo", nombre_var), ("Usuario", usuario_var)):
            tk.Label(panel, text=texto, bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(8, 4))
            tk.Entry(panel, textvariable=variable, font=styles.FONTS["card_text"]).pack(fill="x", ipady=6)

        tk.Label(panel, text="Rol", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        rol_combo = ttk.Combobox(panel, textvariable=rol_var, values=list(roles), state="readonly")
        rol_combo.pack(fill="x", ipady=4)
        tk.Label(panel, text="Estado", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        estado_combo = ttk.Combobox(panel, textvariable=estado_var, values=("ACTIVO", "INACTIVO"), state="readonly")
        estado_combo.pack(fill="x", ipady=4)

        def guardar():
            respuesta = usuarios_controller.actualizar_usuario(
                self.usuario["id_usuario"], usuario["id_usuario"], nombre_var.get(),
                usuario_var.get(), roles.get(rol_var.get()), estado_var.get(),
            )
            if not respuesta["ok"]:
                messagebox.showerror("Editar usuario", respuesta["mensaje"], parent=editor)
                return
            messagebox.showinfo("Editar usuario", respuesta["mensaje"], parent=self)
            editor.destroy()
            self._mostrar_usuarios()

        tk.Button(panel, text="GUARDAR CAMBIOS", command=guardar, bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"], activebackground=styles.COLORS["primary_active"], activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", pady=(20, 8), ipady=8)
        tk.Button(panel, text="CANCELAR", command=editor.destroy, bg=styles.COLORS["secondary"], fg=styles.COLORS["title"], activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", ipady=7)

    def _inactivar_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario is None:
            return
        if not messagebox.askyesno(
            "Inactivar usuario",
            f"¿Desea inactivar a {usuario['nombre_completo']}?\n\nNo podrá iniciar sesión, pero su historial se conservará.",
            parent=self,
        ):
            return
        respuesta = usuarios_controller.eliminar_usuario(self.usuario["id_usuario"], usuario["id_usuario"])
        if not respuesta["ok"]:
            messagebox.showerror("Inactivar usuario", respuesta["mensaje"], parent=self)
            return
        messagebox.showinfo("Inactivar usuario", respuesta["mensaje"], parent=self)
        self._mostrar_usuarios()

    def _mostrar_productos(self, vista=None):
        self.vista_productos = vista or getattr(self, "vista_productos", "tarjetas")
        self.codigo_producto_seleccionado = None
        acceso = "Consulta del catálogo de productos."
        if self.rol in ("ADMIN", "OPERADOR"):
            acceso = "Gestión del catálogo de productos."
        self._limpiar_contenido("Productos")
        self._encabezado("Productos", acceso)

        acciones = tk.Frame(self.contenido, bg=styles.COLORS["background"])
        acciones.pack(fill="x", pady=(0, 16))
        if self.rol in ("ADMIN", "OPERADOR"):
            tk.Button(acciones, text="NUEVO PRODUCTO", command=self._abrir_registro_producto,
                      bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"],
                      activebackground=styles.COLORS["primary_active"], activeforeground=styles.COLORS["button_text"],
                      font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(side="left", ipady=8, ipadx=12)
            tk.Button(acciones, text="EDITAR SELECCIONADO", command=self._abrir_edicion_producto,
                      bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
                      activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"],
                      font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)
            tk.Button(acciones, text="ELIMINAR", command=self._eliminar_producto,
                      bg=styles.COLORS["danger"], fg=styles.COLORS["button_text"],
                      activebackground=styles.COLORS["danger_active"], activeforeground=styles.COLORS["button_text"],
                      font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)
        tk.Button(acciones, text="ACTUALIZAR", command=self._mostrar_productos,
                  bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
                  activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"],
                  font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(side="left", padx=(10, 0), ipady=8, ipadx=12)

        selector = tk.Frame(acciones, bg=styles.COLORS["background"])
        selector.pack(side="right")
        for nombre, modo in (("TARJETAS", "tarjetas"), ("TABLA", "tabla")):
            activo = self.vista_productos == modo
            tk.Button(
                selector,
                text=nombre,
                command=lambda opcion=modo: self._mostrar_productos(opcion),
                bg=styles.COLORS["primary"] if activo else styles.COLORS["secondary"],
                fg=styles.COLORS["button_text"] if activo else styles.COLORS["title"],
                activebackground=styles.COLORS["primary_active"] if activo else styles.COLORS["secondary_active"],
                activeforeground=styles.COLORS["button_text"] if activo else styles.COLORS["title"],
                font=styles.FONTS["button"], relief="flat", bd=0, cursor="hand2",
            ).pack(side="left", padx=(6, 0), ipady=8, ipadx=10)

        respuesta = productos_controller.obtener_productos()
        if not respuesta["ok"]:
            tk.Label(self.contenido, text=respuesta["mensaje"], bg=styles.COLORS["background"],
                     fg=styles.COLORS["danger"], font=styles.FONTS["card_text"]).pack(anchor="w")
            return

        self.productos_por_codigo = {
            producto["codigo"]: producto for producto in respuesta["productos"]
        }
        if self.vista_productos == "tarjetas":
            self._crear_galeria_productos(respuesta["productos"])
            return

        self._crear_tabla_productos(respuesta["productos"])

    def _crear_tabla_productos(self, productos):
        panel = self._crear_panel(self.contenido, padx=12, pady=12)
        panel.pack(fill="both", expand=True)
        columnas = ("codigo", "descripcion", "imagen", "unidad", "presentacion", "precio", "estado", "registro")
        tabla = ttk.Treeview(panel, columns=columnas, show="headings")
        encabezados = {
            "codigo": ("Código", 80), "descripcion": ("Descripción", 220), "imagen": ("Imagen", 85),
            "unidad": ("Unidad", 90), "presentacion": ("Presentación", 105),
            "precio": ("Precio", 80), "estado": ("Estado", 80), "registro": ("Registro", 105),
        }
        for columna in columnas:
            titulo, ancho = encabezados[columna]
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="w")
        for producto in productos:
            fecha = producto["fecha_registro"].strftime("%d/%m/%Y")
            tabla.insert("", "end", values=(
                producto["codigo"], producto["descripcion"], "Disponible" if producto["imagen_url"] else "Sin imagen", producto["unidad_medida"],
                producto["presentacion"], f"Q {producto['precio']}", producto["estado"], fecha,
            ))
        desplazamiento = ttk.Scrollbar(panel, orient="vertical", command=tabla.yview)
        desplazamiento_horizontal = ttk.Scrollbar(panel, orient="horizontal", command=tabla.xview)
        tabla.configure(
            yscrollcommand=desplazamiento.set,
            xscrollcommand=desplazamiento_horizontal.set,
        )
        tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")
        desplazamiento_horizontal.pack(side="bottom", fill="x")
        self.tabla_productos = tabla

    def _crear_galeria_productos(self, productos):
        panel = self._crear_panel(self.contenido, padx=10, pady=10)
        panel.pack(fill="both", expand=True)
        self.tabla_productos = None
        self.tarjetas_producto = {}
        self.imagenes_producto = []

        cabecera = tk.Frame(panel, bg=styles.COLORS["surface"])
        cabecera.pack(fill="x", padx=8, pady=(4, 8))
        self.mensaje_seleccion_producto = tk.Label(
            cabecera,
            text="Seleccione una tarjeta para editarla o inactivarla.",
            bg=styles.COLORS["surface"], fg=styles.COLORS["muted"],
            font=styles.FONTS["card_text"],
        )
        self.mensaje_seleccion_producto.pack(anchor="w")

        canvas = tk.Canvas(panel, bg=styles.COLORS["surface"], highlightthickness=0)
        desplazamiento = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=desplazamiento.set)
        canvas.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")

        galeria = tk.Frame(canvas, bg=styles.COLORS["surface"])
        ventana_galeria = canvas.create_window((0, 0), window=galeria, anchor="nw")

        def actualizar_desplazamiento(_evento=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_ancho(evento):
            canvas.itemconfigure(ventana_galeria, width=evento.width)

        def desplazar_con_rueda(evento):
            if getattr(evento, "num", None) == 4:
                unidades = -3
            elif getattr(evento, "num", None) == 5:
                unidades = 3
            elif evento.delta:
                unidades = -max(1, abs(evento.delta) // 120) if evento.delta > 0 else max(1, abs(evento.delta) // 120)
            else:
                return None
            canvas.yview_scroll(unidades, "units")
            return "break"

        def enlazar_rueda(control):
            control.bind("<MouseWheel>", desplazar_con_rueda, add="+")
            control.bind("<Button-4>", desplazar_con_rueda, add="+")
            control.bind("<Button-5>", desplazar_con_rueda, add="+")

        galeria.bind("<Configure>", actualizar_desplazamiento)
        canvas.bind("<Configure>", ajustar_ancho)
        enlazar_rueda(canvas)
        enlazar_rueda(galeria)
        for columna in range(3):
            galeria.columnconfigure(columna, weight=1, uniform="productos")

        for indice, producto in enumerate(productos):
            fila, columna = divmod(indice, 3)
            tarjeta = tk.Frame(
                galeria,
                bg=styles.COLORS["surface"],
                width=242,
                height=278,
                highlightbackground=styles.COLORS["border"],
                highlightthickness=1,
            )
            tarjeta.grid(row=fila, column=columna, sticky="nsew", padx=8, pady=8)
            tarjeta.grid_propagate(False)
            self.tarjetas_producto[producto["codigo"]] = tarjeta

            imagen = obtener_imagen_producto(producto["imagen_url"])
            if imagen is None:
                vista_imagen = tk.Label(
                    tarjeta, text="SIN IMAGEN", height=6,
                    bg=styles.COLORS["secondary"], fg=styles.COLORS["muted"],
                    font=styles.FONTS["button"],
                )
            else:
                self.imagenes_producto.append(imagen)
                vista_imagen = tk.Label(tarjeta, image=imagen, bg=styles.COLORS["surface"])
                vista_imagen.image = imagen
            vista_imagen.pack(fill="x", padx=10, pady=(10, 8))

            contenido = tk.Frame(tarjeta, bg=styles.COLORS["surface"])
            contenido.pack(fill="both", expand=True, padx=12)
            tk.Label(
                contenido, text=producto["codigo"], bg=styles.COLORS["surface"],
                fg=styles.COLORS["primary"], font=styles.FONTS["button"],
            ).pack(anchor="w")
            tk.Label(
                contenido, text=producto["descripcion"], bg=styles.COLORS["surface"],
                fg=styles.COLORS["title"], font=styles.FONTS["card_title"],
                wraplength=208, justify="left",
            ).pack(anchor="w", pady=(3, 5))
            tk.Label(
                contenido, text=f"{producto['unidad_medida']} | {producto['presentacion']}",
                bg=styles.COLORS["surface"], fg=styles.COLORS["muted"],
                font=styles.FONTS["card_text"],
            ).pack(anchor="w")
            tk.Label(
                contenido, text=f"Q {producto['precio']}", bg=styles.COLORS["surface"],
                fg=styles.COLORS["title"], font=styles.FONTS["card_title"],
            ).pack(anchor="w", pady=(8, 0))

            for control in (tarjeta, vista_imagen, contenido, *contenido.winfo_children()):
                control.bind(
                    "<Button-1>",
                    lambda _evento, codigo=producto["codigo"]: self._seleccionar_tarjeta_producto(codigo),
                )
                enlazar_rueda(control)

    def _seleccionar_tarjeta_producto(self, codigo):
        self.codigo_producto_seleccionado = codigo
        for codigo_tarjeta, tarjeta in self.tarjetas_producto.items():
            seleccionado = codigo_tarjeta == codigo
            tarjeta.configure(
                highlightbackground=styles.COLORS["primary"] if seleccionado else styles.COLORS["border"],
                highlightthickness=2 if seleccionado else 1,
            )
        producto = self.productos_por_codigo[codigo]
        self.mensaje_seleccion_producto.configure(
            text=f"Seleccionado: {producto['codigo']} - {producto['descripcion']}",
            fg=styles.COLORS["primary"],
        )

    def _producto_seleccionado(self):
        if self.tabla_productos is not None:
            seleccion = self.tabla_productos.selection()
            if seleccion:
                valores = self.tabla_productos.item(seleccion[0], "values")
                return self.productos_por_codigo.get(valores[0])
        elif self.codigo_producto_seleccionado:
            return self.productos_por_codigo.get(self.codigo_producto_seleccionado)
        messagebox.showwarning("Productos", "Seleccione un producto de la tabla o una tarjeta.", parent=self)
        return None

    def _abrir_registro_producto(self):
        catalogos = productos_controller.obtener_catalogos_producto()
        if not catalogos["ok"]:
            messagebox.showerror("Productos", catalogos["mensaje"], parent=self)
            return
        unidades = {unidad["nombre"]: unidad["id_unidad"] for unidad in catalogos["unidades"]}
        presentaciones = {
            presentacion["nombre"]: presentacion["id_presentacion"]
            for presentacion in catalogos["presentaciones"]
        }
        if not unidades or not presentaciones:
            messagebox.showerror("Productos", "Debe registrar unidades de medida y presentaciones antes de crear productos.", parent=self)
            return

        editor = tk.Toplevel(self)
        editor.title("Registrar producto")
        editor.geometry("520x700")
        editor.resizable(False, False)
        editor.configure(bg=styles.COLORS["background"])
        editor.transient(self)
        editor.grab_set()
        panel = self._crear_panel(editor, padx=24, pady=18)
        panel.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(panel, text="Registrar producto", bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["card_title"]).pack(anchor="w", pady=(0, 12))

        codigo_var = tk.StringVar()
        descripcion_var = tk.StringVar()
        imagen_url_var = tk.StringVar()
        precio_var = tk.StringVar()
        unidad_var = tk.StringVar()
        presentacion_var = tk.StringVar()
        for texto, variable in (
            ("Código", codigo_var),
            ("Descripción", descripcion_var),
            ("URL de imagen (opcional)", imagen_url_var),
            ("Precio", precio_var),
        ):
            tk.Label(panel, text=texto, bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(8, 4))
            opciones = {}
            if texto == "Precio":
                opciones = {
                    "validate": "key",
                    "validatecommand": (self.register(self._permitir_precio), "%P"),
                }
            tk.Entry(panel, textvariable=variable, font=styles.FONTS["card_text"], **opciones).pack(fill="x", ipady=6)
        tk.Label(panel, text="Unidad de medida", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        ttk.Combobox(panel, textvariable=unidad_var, values=list(unidades), state="readonly").pack(fill="x", ipady=4)
        tk.Label(panel, text="Presentación", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        ttk.Combobox(panel, textvariable=presentacion_var, values=list(presentaciones), state="readonly").pack(fill="x", ipady=4)

        def guardar():
            respuesta = productos_controller.registrar_producto(
                self.usuario["id_usuario"], codigo_var.get(), descripcion_var.get(),
                imagen_url_var.get(), unidades.get(unidad_var.get()),
                presentaciones.get(presentacion_var.get()), precio_var.get(),
            )
            if not respuesta["ok"]:
                messagebox.showerror("Registrar producto", respuesta["mensaje"], parent=editor)
                return
            editor.destroy()
            self._mostrar_productos()
            messagebox.showinfo("Registrar producto", respuesta["mensaje"], parent=self)

        def limpiar():
            codigo_var.set("")
            descripcion_var.set("")
            imagen_url_var.set("")
            precio_var.set("")
            unidad_var.set("")
            presentacion_var.set("")

        tk.Button(panel, text="GUARDAR PRODUCTO", command=guardar, bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"], activebackground=styles.COLORS["primary_active"], activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", pady=(20, 8), ipady=8)
        tk.Button(panel, text="LIMPIAR", command=limpiar, bg=styles.COLORS["secondary"], fg=styles.COLORS["title"], activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", pady=(0, 8), ipady=7)
        tk.Button(panel, text="CANCELAR", command=editor.destroy, bg=styles.COLORS["secondary"], fg=styles.COLORS["title"], activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", ipady=7)

    def _abrir_edicion_producto(self):
        producto = self._producto_seleccionado()
        if producto is None:
            return
        catalogos = productos_controller.obtener_catalogos_producto()
        if not catalogos["ok"]:
            messagebox.showerror("Productos", catalogos["mensaje"], parent=self)
            return
        unidades = {unidad["nombre"]: unidad["id_unidad"] for unidad in catalogos["unidades"]}
        presentaciones = {
            presentacion["nombre"]: presentacion["id_presentacion"]
            for presentacion in catalogos["presentaciones"]
        }

        editor = tk.Toplevel(self)
        editor.title("Editar producto")
        editor.geometry("520x735")
        editor.resizable(False, False)
        editor.configure(bg=styles.COLORS["background"])
        editor.transient(self)
        editor.grab_set()
        panel = self._crear_panel(editor, padx=24, pady=18)
        panel.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(panel, text="Editar producto", bg=styles.COLORS["surface"], fg=styles.COLORS["title"], font=styles.FONTS["card_title"]).pack(anchor="w", pady=(0, 12))

        codigo_var = tk.StringVar(value=producto["codigo"])
        descripcion_var = tk.StringVar(value=producto["descripcion"])
        imagen_url_var = tk.StringVar(value=producto["imagen_url"] or "")
        precio_var = tk.StringVar(value=str(producto["precio"]))
        unidad_var = tk.StringVar(value=producto["unidad_medida"])
        presentacion_var = tk.StringVar(value=producto["presentacion"])
        estado_var = tk.StringVar(value=producto["estado"])

        for texto, variable, editable in (
            ("Código", codigo_var, False),
            ("Descripción", descripcion_var, True),
            ("URL de imagen (opcional)", imagen_url_var, True),
            ("Precio", precio_var, True),
        ):
            tk.Label(panel, text=texto, bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(8, 4))
            opciones = {}
            if texto == "Precio":
                opciones = {
                    "validate": "key",
                    "validatecommand": (self.register(self._permitir_precio), "%P"),
                }
            tk.Entry(
                panel, textvariable=variable, state="normal" if editable else "readonly",
                font=styles.FONTS["card_text"], **opciones,
            ).pack(fill="x", ipady=6)
        tk.Label(panel, text="Unidad de medida", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        ttk.Combobox(panel, textvariable=unidad_var, values=list(unidades), state="readonly").pack(fill="x", ipady=4)
        tk.Label(panel, text="Presentación", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        ttk.Combobox(panel, textvariable=presentacion_var, values=list(presentaciones), state="readonly").pack(fill="x", ipady=4)
        tk.Label(panel, text="Estado", bg=styles.COLORS["surface"], fg=styles.COLORS["text"], font=styles.FONTS["card_text"]).pack(anchor="w", pady=(10, 4))
        ttk.Combobox(panel, textvariable=estado_var, values=("ACTIVO", "INACTIVO"), state="readonly").pack(fill="x", ipady=4)

        def guardar():
            respuesta = productos_controller.actualizar_producto(
                self.usuario["id_usuario"], codigo_var.get(), descripcion_var.get(),
                imagen_url_var.get(), unidades.get(unidad_var.get()),
                presentaciones.get(presentacion_var.get()), precio_var.get(), estado_var.get(),
            )
            if not respuesta["ok"]:
                messagebox.showerror("Editar producto", respuesta["mensaje"], parent=editor)
                return
            editor.destroy()
            self._mostrar_productos()
            messagebox.showinfo("Editar producto", respuesta["mensaje"], parent=self)

        tk.Button(panel, text="GUARDAR CAMBIOS", command=guardar, bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"], activebackground=styles.COLORS["primary_active"], activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", pady=(20, 8), ipady=8)
        tk.Button(panel, text="CANCELAR", command=editor.destroy, bg=styles.COLORS["secondary"], fg=styles.COLORS["title"], activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"], font=styles.FONTS["button"], relief="flat", cursor="hand2").pack(fill="x", ipady=7)

    def _eliminar_producto(self):
        producto = self._producto_seleccionado()
        if producto is None:
            return
        if not messagebox.askyesno(
            "Eliminar producto",
            f"¿Desea eliminar definitivamente {producto['codigo']} - {producto['descripcion']}?\n\n"
            "Esta acción no se puede deshacer.",
            parent=self,
        ):
            return
        respuesta = productos_controller.eliminar_producto(self.usuario["id_usuario"], producto["codigo"])
        if not respuesta["ok"]:
            messagebox.showerror("Eliminar producto", respuesta["mensaje"], parent=self)
            return
        messagebox.showinfo("Eliminar producto", respuesta["mensaje"], parent=self)
        self._mostrar_productos()

    def _mostrar_movimientos(self):
        self._limpiar_contenido("Movimientos")
        self._encabezado(
            "Movimientos",
            "Registre reabastecimientos, salidas por venta y ajustes de inventario.",
        )

        acciones = tk.Frame(self.contenido, bg=styles.COLORS["background"])
        acciones.pack(fill="x", pady=(0, 16))
        tk.Button(
            acciones, text="NUEVO MOVIMIENTO", command=self._abrir_registro_movimiento,
            bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"],
            activebackground=styles.COLORS["primary_active"],
            activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"],
            relief="flat", cursor="hand2",
        ).pack(side="left", ipady=8, ipadx=12)
        tk.Button(
            acciones, text="ACTUALIZAR", command=self._mostrar_movimientos,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"],
            activeforeground=styles.COLORS["title"], font=styles.FONTS["button"],
            relief="flat", cursor="hand2",
        ).pack(side="left", padx=(10, 0), ipady=8, ipadx=12)

        respuesta = inventario_controller.obtener_movimientos()
        if not respuesta["ok"]:
            tk.Label(
                self.contenido, text=respuesta["mensaje"], bg=styles.COLORS["background"],
                fg=styles.COLORS["danger"], font=styles.FONTS["card_text"],
            ).pack(anchor="w")
            return

        panel = self._crear_panel(self.contenido, padx=12, pady=12)
        panel.pack(fill="both", expand=True)
        columnas = ("id", "fecha", "producto", "tipo", "cantidad", "usuario", "observacion")
        tabla = ttk.Treeview(panel, columns=columnas, show="headings")
        encabezados = {
            "id": ("ID", 45), "fecha": ("Fecha", 90), "producto": ("Producto", 195),
            "tipo": ("Movimiento", 145), "cantidad": ("Cantidad", 75),
            "usuario": ("Registrado por", 145), "observacion": ("Observación", 210),
        }
        for columna in columnas:
            titulo, ancho = encabezados[columna]
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="w")

        for movimiento in respuesta["movimientos"]:
            tipo = movimiento["tipo_movimiento"].title()
            if movimiento["tipo_movimiento"] == "SALIDA":
                tipo = "Salida por venta"
            elif movimiento["tipo_movimiento"] == "AJUSTE":
                tipo = f"Ajuste ({movimiento['direccion_ajuste'].lower()})"
            tabla.insert("", "end", values=(
                movimiento["id_movimiento"], movimiento["fecha"].strftime("%d/%m/%Y"),
                f"{movimiento['codigo_producto']} - {movimiento['descripcion']}", tipo,
                movimiento["cantidad"], movimiento["usuario"], movimiento["observacion"] or "",
            ))

        desplazamiento = ttk.Scrollbar(panel, orient="vertical", command=tabla.yview)
        desplazamiento_horizontal = ttk.Scrollbar(panel, orient="horizontal", command=tabla.xview)
        tabla.configure(
            yscrollcommand=desplazamiento.set,
            xscrollcommand=desplazamiento_horizontal.set,
        )
        tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")
        desplazamiento_horizontal.pack(side="bottom", fill="x")

    def _abrir_registro_movimiento(self):
        respuesta = inventario_controller.obtener_productos_inventario()
        if not respuesta["ok"]:
            messagebox.showerror("Movimientos", respuesta["mensaje"], parent=self)
            return
        if not respuesta["productos"]:
            messagebox.showwarning(
                "Movimientos", "Debe registrar al menos un producto activo antes de mover inventario.",
                parent=self,
            )
            return

        productos = {
            f"{producto['codigo']} - {producto['descripcion']}": producto
            for producto in respuesta["productos"]
        }
        editor = tk.Toplevel(self)
        editor.title("Registrar movimiento")
        editor.geometry("520x650")
        editor.resizable(False, False)
        editor.configure(bg=styles.COLORS["background"])
        editor.transient(self)
        editor.grab_set()

        panel = self._crear_panel(editor, padx=24, pady=18)
        panel.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(
            panel, text="Registrar movimiento", bg=styles.COLORS["surface"],
            fg=styles.COLORS["title"], font=styles.FONTS["card_title"],
        ).pack(anchor="w", pady=(0, 4))
        tk.Label(
            panel, text="Las entradas aumentan stock; las salidas por venta lo disminuyen.",
            bg=styles.COLORS["surface"], fg=styles.COLORS["muted"],
            font=styles.FONTS["card_text"],
        ).pack(anchor="w", pady=(0, 8))

        producto_var = tk.StringVar()
        tipo_var = tk.StringVar(value="ENTRADA - Reabastecimiento")
        direccion_var = tk.StringVar()
        cantidad_var = tk.StringVar()
        observacion_var = tk.StringVar()
        stock_var = tk.StringVar(value="Existencia actual: seleccione un producto.")

        def etiqueta(campo):
            tk.Label(
                panel, text=campo, bg=styles.COLORS["surface"],
                fg=styles.COLORS["text"], font=styles.FONTS["card_text"],
            ).pack(anchor="w", pady=(6, 3))

        etiqueta("Producto")
        producto_combo = ttk.Combobox(
            panel, textvariable=producto_var, values=list(productos), state="readonly",
        )
        producto_combo.pack(fill="x", ipady=4)
        tk.Label(
            panel, textvariable=stock_var, bg=styles.COLORS["surface"],
            fg=styles.COLORS["muted"], font=styles.FONTS["card_text"],
        ).pack(anchor="w", pady=(3, 0))

        etiqueta("Tipo de movimiento")
        tipo_combo = ttk.Combobox(
            panel, textvariable=tipo_var,
            values=("ENTRADA - Reabastecimiento", "SALIDA - Venta", "AJUSTE"),
            state="readonly",
        )
        tipo_combo.pack(fill="x", ipady=4)
        etiqueta("Dirección del ajuste")
        direccion_combo = ttk.Combobox(
            panel, textvariable=direccion_var, values=("SUMA", "RESTA"), state="disabled",
        )
        direccion_combo.pack(fill="x", ipady=4)

        etiqueta("Cantidad")
        tk.Entry(
            panel, textvariable=cantidad_var, font=styles.FONTS["card_text"],
            validate="key",
            validatecommand=(self.register(self._permitir_entero), "%P"),
        ).pack(fill="x", ipady=6)
        etiqueta("Observación (opcional)")
        tk.Entry(panel, textvariable=observacion_var, font=styles.FONTS["card_text"]).pack(fill="x", ipady=6)

        def actualizar_producto(_evento=None):
            producto = productos.get(producto_var.get())
            if producto:
                stock_var.set(
                    f"Existencia actual: {producto['existencia']} {producto['unidad_medida']}"
                )

        def actualizar_tipo(_evento=None):
            es_ajuste = tipo_var.get() == "AJUSTE"
            direccion_combo.configure(state="readonly" if es_ajuste else "disabled")
            if not es_ajuste:
                direccion_var.set("")

        producto_combo.bind("<<ComboboxSelected>>", actualizar_producto)
        tipo_combo.bind("<<ComboboxSelected>>", actualizar_tipo)

        def guardar():
            producto = productos.get(producto_var.get())
            tipo = tipo_var.get().split(" ")[0]
            observacion = observacion_var.get()
            if tipo == "SALIDA" and not observacion.strip():
                observacion = "Venta"
            respuesta_guardar = inventario_controller.registrar_movimiento(
                self.usuario["id_usuario"], producto["codigo"] if producto else "", tipo,
                cantidad_var.get(), observacion, direccion_var.get(),
            )
            if not respuesta_guardar["ok"]:
                messagebox.showerror("Registrar movimiento", respuesta_guardar["mensaje"], parent=editor)
                return
            messagebox.showinfo("Registrar movimiento", respuesta_guardar["mensaje"], parent=self)
            editor.destroy()
            self._mostrar_movimientos()

        tk.Button(
            panel, text="GUARDAR MOVIMIENTO", command=guardar,
            bg=styles.COLORS["primary"], fg=styles.COLORS["button_text"],
            activebackground=styles.COLORS["primary_active"], activeforeground=styles.COLORS["button_text"],
            font=styles.FONTS["button"], relief="flat", cursor="hand2",
        ).pack(fill="x", pady=(16, 6), ipady=8)
        tk.Button(
            panel, text="CANCELAR", command=editor.destroy,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"], activeforeground=styles.COLORS["title"],
            font=styles.FONTS["button"], relief="flat", cursor="hand2",
        ).pack(fill="x", ipady=7)

    def _mostrar_reportes(self):
        self._limpiar_contenido("Reportes")
        self._encabezado(
            "Reportes de inventario",
            "Consulte la existencia actual por código, descripción y fecha de registro.",
        )

        filtros = self._crear_panel(self.contenido, padx=18, pady=16)
        filtros.pack(fill="x", pady=(0, 16))
        filtros.columnconfigure((0, 1, 2), weight=1, uniform="filtros")

        codigo_var = tk.StringVar()
        descripcion_var = tk.StringVar()
        fecha_var = tk.StringVar()
        mensaje_var = tk.StringVar()
        campos = (
            ("Código", codigo_var),
            ("Descripción", descripcion_var),
            ("Fecha (AAAA-MM-DD)", fecha_var),
        )
        for columna, (etiqueta, variable) in enumerate(campos):
            tk.Label(
                filtros, text=etiqueta, bg=styles.COLORS["surface"],
                fg=styles.COLORS["text"], font=styles.FONTS["card_text"],
            ).grid(row=0, column=columna, sticky="w", padx=(0, 12) if columna < 2 else 0)
            if etiqueta.startswith("Fecha"):
                campo_fecha = tk.Frame(filtros, bg=styles.COLORS["surface"])
                campo_fecha.grid(
                    row=1, column=columna, sticky="ew", pady=(4, 12),
                )
                campo_fecha.columnconfigure(0, weight=1)
                tk.Entry(
                    campo_fecha, textvariable=variable, font=styles.FONTS["card_text"],
                    bg=styles.COLORS["input"], fg=styles.COLORS["text"],
                    relief="flat", bd=0,
                ).grid(row=0, column=0, sticky="ew", ipady=5)
                tk.Button(
                    campo_fecha, text="CALENDARIO",
                    command=lambda: CalendarioFecha(self, fecha_var),
                    bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
                    activebackground=styles.COLORS["secondary_active"],
                    activeforeground=styles.COLORS["title"],
                    font=styles.FONTS["button"], relief="flat", bd=0,
                    cursor="hand2",
                ).grid(row=0, column=1, padx=(6, 0), ipady=5)
            else:
                tk.Entry(
                    filtros, textvariable=variable, font=styles.FONTS["card_text"],
                    bg=styles.COLORS["input"], fg=styles.COLORS["text"],
                    relief="flat", bd=0,
                ).grid(
                    row=1, column=columna, sticky="ew", padx=(0, 12) if columna < 2 else 0,
                    pady=(4, 12), ipady=5,
                )

        panel = self._crear_panel(self.contenido, padx=12, pady=12)
        panel.pack(fill="both", expand=True)
        columnas = ("codigo", "fecha", "descripcion", "cantidad", "presentacion", "unidad", "precio")
        tabla = ttk.Treeview(panel, columns=columnas, show="headings")
        encabezados = {
            "codigo": ("CÓDIGO", 85), "fecha": ("FECHA", 95),
            "descripcion": ("DESCRIPCIÓN", 200), "cantidad": ("CANTIDAD", 85),
            "presentacion": ("PRESENTACIÓN", 110), "unidad": ("UNIDAD MEDIDA", 120),
            "precio": ("PRECIO", 90),
        }
        for columna in columnas:
            titulo, ancho = encabezados[columna]
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="w")

        desplazamiento = ttk.Scrollbar(panel, orient="vertical", command=tabla.yview)
        desplazamiento_horizontal = ttk.Scrollbar(panel, orient="horizontal", command=tabla.xview)
        tabla.configure(
            yscrollcommand=desplazamiento.set,
            xscrollcommand=desplazamiento_horizontal.set,
        )
        tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")
        desplazamiento_horizontal.pack(side="bottom", fill="x")

        def buscar():
            respuesta = inventario_controller.obtener_reporte_inventario(
                codigo_var.get(), descripcion_var.get(), fecha_var.get()
            )
            for item in tabla.get_children():
                tabla.delete(item)
            if not respuesta["ok"]:
                mensaje_var.set(respuesta["mensaje"])
                return
            mensaje_var.set(
                f"{len(respuesta['registros'])} producto(s) encontrado(s). "
                "La cantidad corresponde a la existencia actual."
            )
            for registro in respuesta["registros"]:
                tabla.insert("", "end", values=(
                    registro["codigo"], registro["fecha"].strftime("%d/%m/%Y"),
                    registro["descripcion"], registro["cantidad"],
                    registro["presentacion"], registro["unidad_medida"],
                    f"Q {registro['precio']}",
                ))

        def limpiar_filtros():
            codigo_var.set("")
            descripcion_var.set("")
            fecha_var.set("")
            buscar()

        tk.Button(
            filtros, text="BUSCAR", command=buscar, bg=styles.COLORS["primary"],
            fg=styles.COLORS["button_text"], activebackground=styles.COLORS["primary_active"],
            activeforeground=styles.COLORS["button_text"], font=styles.FONTS["button"],
            relief="flat", cursor="hand2",
        ).grid(row=2, column=0, sticky="w", ipady=7, ipadx=16)
        tk.Button(
            filtros, text="LIMPIAR", command=limpiar_filtros, bg=styles.COLORS["secondary"],
            fg=styles.COLORS["title"], activebackground=styles.COLORS["secondary_active"],
            activeforeground=styles.COLORS["title"], font=styles.FONTS["button"],
            relief="flat", cursor="hand2",
        ).grid(row=2, column=1, sticky="w", ipady=7, ipadx=16)
        tk.Button(
            filtros, text="CANCELAR", command=self._mostrar_inicio,
            bg=styles.COLORS["secondary"], fg=styles.COLORS["title"],
            activebackground=styles.COLORS["secondary_active"],
            activeforeground=styles.COLORS["title"], font=styles.FONTS["button"],
            relief="flat", cursor="hand2",
        ).grid(row=2, column=2, sticky="w", ipady=7, ipadx=16)
        tk.Label(
            filtros, textvariable=mensaje_var, bg=styles.COLORS["surface"],
            fg=styles.COLORS["muted"], font=styles.FONTS["card_text"],
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(12, 0))

        buscar()

    def _abrir_usuarios(self):
        RegisterView(self, administrador=self.usuario)

    def _cerrar_sesion(self):
        self.destroy()
        self.al_cerrar_sesion()
