import tkinter as tk
from tkinter import ttk, messagebox

from models.contacto import Contacto
from persistencia.gestor_indice import GestorIndice
from persistencia.gestor_archivos import GestorArchivos
from servicios.servicio_integridad import ServicioIntegridad
from servicios.servicio_archivos_sistema import ServicioArchivosSistema
from servicios.servicio_exportacion import ServicioExportacion


PALETAS = {
    "dark": {
        "bg_main": "#0f172a",
        "bg_card": "#1e293b",
        "bg_input": "#0b1120",
        "fg_primary": "#f8fafc",
        "fg_secondary": "#94a3b8",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#334155",
        "console_bg": "#090d16",
        "console_fg": "#38bdf8",
    },
    "light": {
        "bg_main": "#f1f5f9",
        "bg_card": "#ffffff",
        "bg_input": "#f8fafc",
        "fg_primary": "#0f172a",
        "fg_secondary": "#475569",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "success": "#059669",
        "warning": "#d97706",
        "danger": "#dc2626",
        "border": "#cbd5e1",
        "console_bg": "#0f172a",
        "console_fg": "#38bdf8",
    },
}


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda de Contactos — Acceso Aleatorio & Hashing SHA-256")
        self.geometry("1020x680")
        self.minsize(940, 620)

        # Estado del tema 
        self.tema_actual = "dark"

        # Instancias de persistencia y servicios
        self.gestor_indice = GestorIndice()
        self.gestor_archivos = GestorArchivos(gestor_indice=self.gestor_indice)
        self.servicio_integridad = ServicioIntegridad()
        self.servicio_sistema = ServicioArchivosSistema()
        self.servicio_exportacion = ServicioExportacion()

        # Variables de formulario
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_ciudad = tk.StringVar()

        # Variables de telemetría 
        self.var_num_registro = tk.StringVar(value="—")
        self.var_offset_tell = tk.StringVar(value="0 B")
        self.var_tamano_fijo = tk.StringVar(value=f"{Contacto.TAMANO_REGISTRO} B")
        self.var_estado_hash = tk.StringVar(value="Verificando...")
        self.var_barra_estado = tk.StringVar(value="Sistema listo | Codificación UTF-8 | Acceso Directo O(1)")

        self.estilo = ttk.Style(self)
        self.estilo.theme_use("clam")

        self._crear_menu()
        self._construir_interfaz()
        self._aplicar_tema()
        self._actualizar_tabla_indice()

    # CONSTRUCCIÓN VISUAL Y SISTEMA DE TEMAS

    def _crear_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        # 1. Menú Contactos
        menu_contactos = tk.Menu(barra_menu, tearoff=0)
        menu_contactos.add_command(label="Agregar contacto", command=self.on_agregar_contacto, accelerator="Ctrl+N")
        menu_contactos.add_command(label="Buscar por ID", command=self.on_buscar_contacto, accelerator="Ctrl+F")
        menu_contactos.add_command(label="Modificar contacto", command=self.on_modificar_contacto, accelerator="Ctrl+M")
        menu_contactos.add_separator()
        menu_contactos.add_command(label="Limpiar formulario", command=self.limpiar_formulario, accelerator="Esc")
        menu_contactos.add_separator()
        menu_contactos.add_command(label="Salir", command=self.quit)
        barra_menu.add_cascade(label="Contactos", menu=menu_contactos)

        # 2. Menú Exportar
        menu_exportar = tk.Menu(barra_menu, tearoff=0)
        menu_exportar.add_command(label="Exportar a JSON", command=self.on_exportar_json)
        menu_exportar.add_command(label="Generar reporte PDF", command=self.on_generar_pdf)
        barra_menu.add_cascade(label="Exportar", menu=menu_exportar)

        # 3. Menú Herramientas
        menu_herramientas = tk.Menu(barra_menu, tearoff=0)
        menu_herramientas.add_command(label="Verificar integridad (SHA-256)", command=self.on_verificar_integridad)
        menu_herramientas.add_command(label="Crear respaldo ZIP", command=self.on_crear_respaldo_zip)
        menu_herramientas.add_separator()
        menu_herramientas.add_command(label="Información del archivo...", command=self.on_mostrar_info_archivo)
        barra_menu.add_cascade(label="Herramientas", menu=menu_herramientas)

        # 4. Menú Ayuda (Simulado)
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Estructura del registro fijo", command=self.on_mostrar_ayuda)
        menu_ayuda.add_command(label="Acerca de...", command=self.on_mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.bind("<Control-n>", lambda e: self.on_agregar_contacto())
        self.bind("<Control-f>", lambda e: self.on_buscar_contacto())
        self.bind("<Control-m>", lambda e: self.on_modificar_contacto())
        self.bind("<Escape>", lambda e: self.limpiar_formulario())

    def _construir_interfaz(self):
        # Contenedor raíz
        self.frame_raiz = ttk.Frame(self, style="Main.TFrame", padding=16)
        self.frame_raiz.pack(fill=tk.BOTH, expand=True)
        self.frame_raiz.columnconfigure(0, weight=5)
        self.frame_raiz.columnconfigure(1, weight=6)
        self.frame_raiz.rowconfigure(2, weight=1)

        # 1. ENCABEZADO SUPERIOR
        self.frame_header = ttk.Frame(self.frame_raiz, style="Card.TFrame", padding=(16, 12))
        self.frame_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.frame_header.columnconfigure(0, weight=1)

        box_titulos = ttk.Frame(self.frame_header, style="Card.TFrame")
        box_titulos.grid(row=0, column=0, sticky="w")
        ttk.Label(box_titulos, text="AGENDA DE CONTACTOS", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(
            box_titulos,
            text="Gestión de Archivos",
            style="SubTitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Botonera rápida de cabecera + Toggle Tema
        box_acciones_top = ttk.Frame(self.frame_header, style="Card.TFrame")
        box_acciones_top.grid(row=0, column=1, sticky="e")

        ttk.Button(
            box_acciones_top, text="Exportar JSON", style="Secondary.TButton", cursor="hand2", command=self.on_exportar_json
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            box_acciones_top, text="Reporte PDF", style="Secondary.TButton", cursor="hand2", command=self.on_generar_pdf
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            box_acciones_top, text="Respaldo ZIP", style="Secondary.TButton", cursor="hand2", command=self.on_crear_respaldo_zip
        ).pack(side=tk.LEFT, padx=4)
        self.btn_tema = ttk.Button(
            box_acciones_top, text="Modo Claro", style="Accent.TButton", cursor="hand2", command=self.alternar_tema
        )
        self.btn_tema.pack(side=tk.LEFT, padx=(10, 0))

        # 2. FILA DE TARJETAS DE TELEMETRÍA (KPIs de Acceso Aleatorio)
        self.frame_kpis = ttk.Frame(self.frame_raiz, style="Main.TFrame")
        self.frame_kpis.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.frame_kpis.columnconfigure((0, 1, 2, 3), weight=1)

        self._crear_kpi_card(self.frame_kpis, 0, "NÚMERO DE REGISTRO", self.var_num_registro, "Posición en índice JSON")
        self._crear_kpi_card(self.frame_kpis, 1, "PUNTERO tell/seek", self.var_offset_tell, "Desplazamiento exacto")
        self._crear_kpi_card(self.frame_kpis, 2, "LONGITUD DE BLOQUE", self.var_tamano_fijo, "Relleno fijo con ljust")
        self._crear_kpi_card(self.frame_kpis, 3, "INTEGRIDAD SHA-256", self.var_estado_hash, "Huella de contactos.dat")

        # 3. COLUMNA IZQUIERDA: FORMULARIO + INSPECTOR DE BLOQUE FIJO
        frame_izq = ttk.Frame(self.frame_raiz, style="Main.TFrame")
        frame_izq.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        frame_izq.columnconfigure(0, weight=1)
        frame_izq.rowconfigure(1, weight=1)

        # Tarjeta de Formulario
        card_form = ttk.Frame(frame_izq, style="Card.TFrame", padding=18)
        card_form.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        card_form.columnconfigure(1, weight=1)

        ttk.Label(card_form, text="Registro y Edición de Contacto", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        # Campo ID con botón de búsqueda rápida
        ttk.Label(card_form, text="ID Contacto (10B):", style="Form.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        box_id = ttk.Frame(card_form, style="Card.TFrame")
        box_id.grid(row=1, column=1, sticky="ew", pady=6, padx=(12, 0))
        box_id.columnconfigure(0, weight=1)

        self.entry_id = ttk.Entry(box_id, textvariable=self.var_id, font=("Consolas", 10, "bold"))
        self.entry_id.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=3)
        ttk.Button(
            box_id, text="Buscar con seek", style="Accent.TButton", cursor="hand2", command=self.on_buscar_contacto
        ).grid(row=0, column=1)

        campos_meta = [
            ("Nombre (35B):", self.var_nombre, 2),
            ("Teléfono (15B):", self.var_telefono, 3),
            ("Correo (35B):", self.var_correo, 4),
            ("Ciudad (25B):", self.var_ciudad, 5),
        ]
        for etiqueta, variable, fila in campos_meta:
            ttk.Label(card_form, text=etiqueta, style="Form.TLabel").grid(row=fila, column=0, sticky="w", pady=6)
            entry = ttk.Entry(card_form, textvariable=variable, font=("Segoe UI", 10))
            entry.grid(row=fila, column=1, sticky="ew", pady=6, padx=(12, 0), ipady=3)

        # Botonera principal del formulario
        box_botones = ttk.Frame(card_form, style="Card.TFrame")
        box_botones.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        box_botones.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(
            box_botones, text="+ Agregar Contacto", style="Primary.TButton", cursor="hand2", command=self.on_agregar_contacto
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=4)
        ttk.Button(
            box_botones, text="Modificar ", style="Warning.TButton", cursor="hand2", command=self.on_modificar_contacto
        ).grid(row=0, column=1, sticky="ew", padx=5, ipady=4)
        ttk.Button(
            box_botones, text="Limpiar", style="Secondary.TButton", cursor="hand2", command=self.limpiar_formulario
        ).grid(row=0, column=2, sticky="ew", padx=(5, 0), ipady=4)

        # Tarjeta de Vista Previa del Registro Crudo de 120 Bytes
        card_raw = ttk.Frame(frame_izq, style="Card.TFrame", padding=14)
        card_raw.grid(row=1, column=0, sticky="nsew")
        card_raw.columnconfigure(0, weight=1)
        card_raw.rowconfigure(1, weight=1)

        ttk.Label(
            card_raw,
            text="Vista Previa de Registro Fijo (120 Bytes - '·' representa espacio de relleno)",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.txt_bloque_raw = tk.Text(
            card_raw, height=3, font=("Consolas", 9), wrap="char", state="disabled", relief=tk.FLAT, padx=8, pady=6
        )
        self.txt_bloque_raw.grid(row=1, column=0, sticky="nsew")

        # 4. COLUMNA DERECHA: ÍNDICE PRIMARIO EN VIVO + BITÁCORA
        frame_der = ttk.Frame(self.frame_raiz, style="Main.TFrame")
        frame_der.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        frame_der.columnconfigure(0, weight=1)
        frame_der.rowconfigure(0, weight=3)
        frame_der.rowconfigure(1, weight=2)

        # Tarjeta del Índice Primario (indice.json)
        card_indice = ttk.Frame(frame_der, style="Card.TFrame", padding=16)
        card_indice.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        card_indice.columnconfigure(0, weight=1)
        card_indice.rowconfigure(1, weight=1)

        header_indice = ttk.Frame(card_indice, style="Card.TFrame")
        header_indice.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        header_indice.columnconfigure(0, weight=1)

        ttk.Label(
            header_indice,
            text="Índice Primario en Vivo",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(
            header_indice, text="Metadatos", style="Secondary.TButton", cursor="hand2", command=self.on_mostrar_info_archivo
        ).grid(row=0, column=1, sticky="e")

        columnas = ("id", "num_reg", "offset_bytes")
        self.tabla_indice = ttk.Treeview(card_indice, columns=columnas, show="headings", height=6)
        self.tabla_indice.heading("id", text="ID Contacto")
        self.tabla_indice.heading("num_reg", text="Núm. Registro")
        self.tabla_indice.heading("offset_bytes", text="Ubicacion")

        self.tabla_indice.column("id", width=100, anchor="center")
        self.tabla_indice.column("num_reg", width=110, anchor="center")
        self.tabla_indice.column("offset_bytes", width=160, anchor="center")
        self.tabla_indice.grid(row=1, column=0, sticky="nsew")

        scroll_tabla = ttk.Scrollbar(card_indice, orient=tk.VERTICAL, command=self.tabla_indice.yview)
        self.tabla_indice.configure(yscrollcommand=scroll_tabla.set)
        scroll_tabla.grid(row=1, column=1, sticky="ns")

        self.tabla_indice.bind("<Double-1>", self._on_doble_clic_indice)

        # Tarjeta de Consola / Bitácora de Operaciones de Puntero
        card_bitacora = ttk.Frame(frame_der, style="Card.TFrame", padding=16)
        card_bitacora.grid(row=1, column=0, sticky="nsew")
        card_bitacora.columnconfigure(0, weight=1)
        card_bitacora.rowconfigure(1, weight=1)

        header_bitacora = ttk.Frame(card_bitacora, style="Card.TFrame")
        header_bitacora.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header_bitacora.columnconfigure(0, weight=1)

        ttk.Label(header_bitacora, text="Bitácora de Punteros y Operaciones", style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(
            header_bitacora, text="Verificar SHA-256", style="Secondary.TButton", cursor="hand2", command=self.on_verificar_integridad
        ).grid(row=0, column=1, sticky="e")

        self.txt_bitacora = tk.Text(
            card_bitacora, height=6, font=("Consolas", 9), state="disabled", relief=tk.FLAT, padx=10, pady=8
        )
        self.txt_bitacora.grid(row=1, column=0, sticky="nsew")

        # 5. BARRA DE ESTADO INFERIOR
        self.barra_estado = ttk.Label(
            self.frame_raiz, textvariable=self.var_barra_estado, style="Status.TLabel", padding=(10, 5)
        )
        self.barra_estado.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _crear_kpi_card(self, padre, columna, titulo, variable_valor, subtitulo):
        card = ttk.Frame(padre, style="Card.TFrame", padding=(14, 10))
        card.grid(row=0, column=columna, sticky="nsew", padx=(0 if columna == 0 else 6, 0 if columna == 3 else 6))
        ttk.Label(card, text=titulo, style="KpiTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable_valor, style="KpiValue.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(card, text=subtitulo, style="KpiSub.TLabel").pack(anchor="w")

    def alternar_tema(self):
        self.tema_actual = "light" if self.tema_actual == "dark" else "dark"
        texto_boton = "Modo Oscuro" if self.tema_actual == "light" else "☀ Modo Claro"
        self.btn_tema.configure(text=texto_boton)
        self._aplicar_tema()

    def _aplicar_tema(self):
        p = PALETAS[self.tema_actual]
        self.configure(bg=p["bg_main"])

        self.estilo.configure("Main.TFrame", background=p["bg_main"])
        self.estilo.configure("Card.TFrame", background=p["bg_card"], relief="flat")

        self.estilo.configure("HeaderTitle.TLabel", background=p["bg_card"], foreground=p["fg_primary"], font=("Segoe UI", 14, "bold"))
        self.estilo.configure("SubTitle.TLabel", background=p["bg_card"], foreground=p["fg_secondary"], font=("Segoe UI", 9))
        self.estilo.configure("SectionTitle.TLabel", background=p["bg_card"], foreground=p["fg_primary"], font=("Segoe UI", 10, "bold"))
        self.estilo.configure("Form.TLabel", background=p["bg_card"], foreground=p["fg_secondary"], font=("Segoe UI", 9, "bold"))

        self.estilo.configure("KpiTitle.TLabel", background=p["bg_card"], foreground=p["fg_secondary"], font=("Segoe UI", 8, "bold"))
        self.estilo.configure("KpiValue.TLabel", background=p["bg_card"], foreground=p["accent"], font=("Consolas", 14, "bold"))
        self.estilo.configure("KpiSub.TLabel", background=p["bg_card"], foreground=p["fg_secondary"], font=("Segoe UI", 8))

        self.estilo.configure("Status.TLabel", background=p["bg_card"], foreground=p["fg_secondary"], font=("Segoe UI", 9))

        # Entradas de texto
        self.estilo.configure(
            "TEntry",
            fieldbackground=p["bg_input"],
            foreground=p["fg_primary"],
            bordercolor=p["border"],
            lightcolor=p["border"],
            darkcolor=p["border"],
            insertcolor=p["fg_primary"],
        )

        # Botones semánticos
        self.estilo.configure("Primary.TButton", background=p["success"], foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 5))
        self.estilo.map("Primary.TButton", background=[("active", "#059669")])

        self.estilo.configure("Accent.TButton", background=p["accent"], foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 5))
        self.estilo.map("Accent.TButton", background=[("active", p["accent_hover"])])

        self.estilo.configure("Warning.TButton", background=p["warning"], foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 5))
        self.estilo.map("Warning.TButton", background=[("active", "#d97706")])

        self.estilo.configure("Secondary.TButton", background=p["border"], foreground=p["fg_primary"], font=("Segoe UI", 9), borderwidth=0, padding=(10, 5))
        self.estilo.map("Secondary.TButton", background=[("active", p["accent"]), ("active", "#ffffff")])

        # Tabla Treeview
        self.estilo.configure(
            "Treeview",
            background=p["bg_input"],
            foreground=p["fg_primary"],
            fieldbackground=p["bg_input"],
            rowheight=26,
            font=("Consolas", 9),
            borderwidth=0,
        )
        self.estilo.configure(
            "Treeview.Heading",
            background=p["border"],
            foreground=p["fg_primary"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        self.estilo.map("Treeview", background=[("selected", p["accent"])], foreground=[("selected", "#ffffff")])

        # Cajas de texto de consola y bloque fijo
        self.txt_bitacora.configure(bg=p["console_bg"], fg=p["console_fg"], insertbackground=p["fg_primary"])
        self.txt_bloque_raw.configure(bg=p["bg_input"], fg=p["fg_primary"])

    # UTILIDADES VISUALES Y DE DATOS

    def registrar_evento(self, mensaje: str):
        self.txt_bitacora.configure(state="normal")
        self.txt_bitacora.insert(tk.END, f"› {mensaje}\n")
        self.txt_bitacora.see(tk.END)
        self.txt_bitacora.configure(state="disabled")
        self.var_barra_estado.set(mensaje)

    def _mostrar_bloque_raw(self, contacto: Contacto | None):
        self.txt_bloque_raw.configure(state="normal")
        self.txt_bloque_raw.delete("1.0", tk.END)
        if contacto is not None:
            cadena_fija = contacto.a_registro_fijo()
            visual = cadena_fija.replace(" ", "·")
            self.txt_bloque_raw.insert(tk.END, f"[{len(cadena_fija.encode('utf-8'))}B] {visual}")
        else:
            self.txt_bloque_raw.insert(tk.END, "Seleccione o busque un contacto para inspeccionar sus 120 bytes fijos...")
        self.txt_bloque_raw.configure(state="disabled")

    def _actualizar_tabla_indice(self):
        for item in self.tabla_indice.get_children():
            self.tabla_indice.delete(item)
        try:
            indice = self.gestor_indice.cargar_indice()
            for id_str, num_reg in sorted(indice.items(), key=lambda x: int(x[0])):
                offset = num_reg * Contacto.TAMANO_REGISTRO
                self.tabla_indice.insert("", tk.END, values=(id_str, f"Registro #{num_reg}", f"Byte {offset}"))
        except Exception as e:
            self.registrar_evento(f"Aviso al leer índice: {e}")

    def _on_doble_clic_indice(self, _evento):
        seleccion = self.tabla_indice.selection()
        if not seleccion:
            return
        valores = self.tabla_indice.item(seleccion[0], "values")
        if valores:
            self.var_id.set(str(valores[0]))
            self.on_buscar_contacto()

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_telefono.set("")
        self.var_correo.set("")
        self.var_ciudad.set("")
        self.var_num_registro.set("—")
        self.var_offset_tell.set("0 B")
        self._mostrar_bloque_raw(None)
        self.entry_id.focus_set()
        self.registrar_evento("Formulario limpio.")

    def obtener_datos_formulario(self, validar_todos=True):
        id_str = self.var_id.get().strip()
        if not id_str.isdigit():
            messagebox.showwarning("ID inválido", "El campo ID debe ser un número entero positivo.")
            return None

        datos = {
            "id": int(id_str),
            "nombre": self.var_nombre.get().strip(),
            "telefono": self.var_telefono.get().strip(),
            "correo": self.var_correo.get().strip(),
            "ciudad": self.var_ciudad.get().strip(),
        }

        if validar_todos and not all([datos["nombre"], datos["telefono"], datos["correo"], datos["ciudad"]]):
            messagebox.showwarning("Campos incompletos", "Todos los campos del contacto son obligatorios.")
            return None

        return datos

    # OPERACIONES DE ARCHIVO Y ACCESO ALEATORIO

    def on_agregar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=True)
        if not datos:
            return

        try:
            nuevo_contacto = Contacto(
                datos["id"], datos["nombre"], datos["telefono"], datos["correo"], datos["ciudad"]
            )
            num_reg, pos_tell = self.gestor_archivos.agregar_contacto(nuevo_contacto)
            nuevo_hash = self.servicio_integridad.actualizar_hash()

            self.var_num_registro.set(f"#{num_reg}")
            self.var_offset_tell.set(f"{pos_tell} B")
            self.var_estado_hash.set(f"OK ({nuevo_hash[:8]}…)")
            self._mostrar_bloque_raw(nuevo_contacto)
            self._actualizar_tabla_indice()

            self.registrar_evento(f"Agregado ID {datos['id']} -> Reg #{num_reg} | tell() = {pos_tell} bytes.")
            messagebox.showinfo(
                "Contacto Registrado",
                f"Contacto guardado en contactos.dat\n\n• Número de registro: {num_reg}\n• Posición tell(): {pos_tell} bytes",
            )
        except (ValueError, PermissionError, RuntimeError) as e:
            self.registrar_evento(f"Error al agregar: {e}")
            messagebox.showerror("Error al guardar", str(e))

    def on_buscar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=False)
        if not datos:
            return

        try:
            contacto, num_reg, pos_tell = self.gestor_archivos.buscar_por_id(datos["id"])
            self.var_nombre.set(contacto.nombre)
            self.var_telefono.set(contacto.telefono)
            self.var_correo.set(contacto.correo)
            self.var_ciudad.set(contacto.ciudad)

            self.var_num_registro.set(f"#{num_reg}")
            self.var_offset_tell.set(f"{pos_tell} B")
            self._mostrar_bloque_raw(contacto)

            self.registrar_evento(f"Acceso directo ID {datos['id']} - Registro #{num_reg} | seek/tell = {pos_tell} bytes.")
        except KeyError as e:
            self.registrar_evento(f"Búsqueda fallida: ID {datos['id']} no existe en indice.json.")
            messagebox.showwarning("ID no encontrado", str(e).strip("'"))
        except (FileNotFoundError, PermissionError, RuntimeError, ValueError) as e:
            self.registrar_evento(f"Error en búsqueda: {e}")
            messagebox.showerror("Error de lectura", str(e))

    def on_modificar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=True)
        if not datos:
            return

        try:
            contacto_editado = Contacto(
                datos["id"], datos["nombre"], datos["telefono"], datos["correo"], datos["ciudad"]
            )
            num_reg, pos_tell = self.gestor_archivos.modificar_contacto(contacto_editado)
            nuevo_hash = self.servicio_integridad.actualizar_hash()

            self.var_num_registro.set(f"#{num_reg}")
            self.var_offset_tell.set(f"{pos_tell} B")
            self.var_estado_hash.set(f"OK ({nuevo_hash[:8]}…)")
            self._mostrar_bloque_raw(contacto_editado)

            self.registrar_evento(f"Sobrescritura in-situ ID {datos['id']} en Reg #{num_reg} (tell={pos_tell}B).")
            messagebox.showinfo(
                "Modificación en el Lugar",
                f"Registro #{num_reg} sobrescrito directamente en el byte {pos_tell} sin reescribir el archivo.",
            )
        except KeyError as e:
            self.registrar_evento(f"Error: ID {datos['id']} no existe para modificar.")
            messagebox.showwarning("ID inexistente", str(e).strip("'"))
        except (FileNotFoundError, PermissionError, RuntimeError) as e:
            self.registrar_evento(f"Error al modificar: {e}")
            messagebox.showerror("Error de archivo", str(e))

    # EXPORTACIÓN, INTEGRIDAD Y METADATOS
    def on_exportar_json(self):
        try:
            contactos = self.gestor_archivos.listar_todos()
            if not contactos:
                messagebox.showwarning("Sin datos", "No hay contactos registrados para exportar.")
                return
            ruta = self.servicio_exportacion.exportar_a_json(contactos)
            self.registrar_evento(f"Exportados {len(contactos)} registros a {ruta}.")
            messagebox.showinfo("Exportación JSON", f"Archivo JSON generado correctamente:\n{ruta}")
        except (FileNotFoundError, PermissionError, RuntimeError) as e:
            self.registrar_evento(f"Error exportando JSON: {e}")
            messagebox.showerror("Error de exportación", str(e))

    def on_generar_pdf(self):
        try:
            ruta_pdf = self.servicio_exportacion.generar_pdf_desde_json()
            self.registrar_evento(f"Reporte PDF generado con ReportLab Canvas en {ruta_pdf}.")
            messagebox.showinfo("Reporte PDF", f"Reporte PDF generado exitosamente en:\n{ruta_pdf}")
        except (FileNotFoundError, PermissionError, RuntimeError) as e:
            self.registrar_evento(f"Error generando PDF: {e}")
            messagebox.showerror("Error en PDF", str(e))

    def on_verificar_integridad(self, silencioso=False):
        try:
            es_valido, mensaje = self.servicio_integridad.verificar_integridad()
            if es_valido:
                self.var_estado_hash.set("ÍNTEGRO")
                self.registrar_evento(f"SHA-256 verificado: {mensaje}")
                if not silencioso:
                    messagebox.showinfo("Integridad SHA-256", mensaje)
            else:
                self.var_estado_hash.set("¡ALTERADO!")
                self.registrar_evento(f"ALERTA DE INTEGRIDAD: {mensaje}")
                messagebox.showwarning("Alerta de Seguridad SHA-256", mensaje)
        except PermissionError as e:
            self.var_estado_hash.set("Sin Permisos")
            self.registrar_evento(str(e))
            messagebox.showerror("Error de permisos", str(e))

    def on_crear_respaldo_zip(self):
        try:
            info = self.servicio_sistema.crear_respaldo_zip()
            orig = info["tamano_original"]
            comp = info["tamano_comprimido"]
            ahorro = ((orig - comp) / orig * 100) if orig > 0 else 0.0

            self.registrar_evento(f"Respaldo ZIP: {orig}B -> {comp}B ({ahorro:.1f}% comprimido).")
            messagebox.showinfo(
                "Respaldo Comprimido ZIP",
                f"Archivo creado: {info['ruta_zip']}\n\n"
                f"Tamaño original (contactos.dat + indice.json): {orig} bytes\n"
                f"Tamaño comprimido (ZIP): {comp} bytes\n"
                f"Proporción de ahorro: {ahorro:.1f}%",
            )
        except (FileNotFoundError, PermissionError) as e:
            self.registrar_evento(f"Error al respaldar en ZIP: {e}")
            messagebox.showerror("Error en Respaldo ZIP", str(e))

    def on_mostrar_info_archivo(self):
        try:
            meta = self.servicio_sistema.obtener_metadatos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron leer los metadatos: {e}")
            return

        p = PALETAS[self.tema_actual]
        ventana = tk.Toplevel(self)
        ventana.title("Metadatos y Permisos")
        ventana.geometry("440x270")
        ventana.resizable(False, False)
        ventana.configure(bg=p["bg_main"])
        ventana.transient(self)
        ventana.grab_set()

        card = ttk.Frame(ventana, style="Card.TFrame", padding=20)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        ttk.Label(card, text="Información del Archivo de Datos", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        filas = [
            ("Ruta del archivo:", meta["archivo"]),
            ("Estado en disco:", "Creado y disponible" if meta["existe"] else "No existe aún"),
            ("Tamaño exacto:", f"{meta['tamano_bytes']} bytes"),
            ("Última modificación:", meta["ultima_modificacion"]),
            ("Permiso Lectura:", "Concedido" if meta["permiso_lectura"] else "✖ Denegado"),
            ("Permiso Escritura:", "Concedido" if meta["permiso_escritura"] else "✖ Denegado"),
        ]

        for idx, (etiq, val) in enumerate(filas, start=1):
            ttk.Label(card, text=etiq, style="Form.TLabel").grid(row=idx, column=0, sticky="w", pady=4)
            ttk.Label(card, text=val, style="SubTitle.TLabel").grid(row=idx, column=1, sticky="w", padx=(14, 0), pady=4)

        ttk.Button(card, text="Cerrar", style="Accent.TButton", cursor="hand2", command=ventana.destroy).grid(
            row=len(filas) + 1, column=0, columnspan=2, pady=(16, 0)
        )

    def on_mostrar_ayuda(self):
        mensaje = (
            f"Estructura Documentada del Registro ({Contacto.TAMANO_REGISTRO} bytes en UTF-8):\n\n"
            f"- ID: {Contacto.LEN_ID} bytes\n"
            f"- Nombre: {Contacto.LEN_NOMBRE} bytes\n"
            f"- Teléfono: {Contacto.LEN_TELEFONO} bytes\n"
            f"- Correo: {Contacto.LEN_CORREO} bytes\n"
            f"- Ciudad: {Contacto.LEN_CIUDAD} bytes\n\n"
            "Cálculo de Acceso Directo:\n"
            "numero_registro * 120"
        )
        messagebox.showinfo("Estructura del Registro", mensaje)

    def on_mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Agenda de Contactos con Acceso Aleatorio\n"
            "Ingeniería en Informática y Sistemas — URL\n"
            "Proyecto No. 2 — Manejo de Archivos",
        )