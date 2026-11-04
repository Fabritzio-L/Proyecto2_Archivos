import tkinter as tk
from tkinter import ttk, messagebox


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda de Contactos - Acceso Aleatorio")
        self.geometry("760x520")
        self.minsize(720, 480)
        self.configure(padx=15, pady=15)

        # Variables de estado vinculadas a los campos del contacto
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_ciudad = tk.StringVar()

        # Variables informativas de acceso aleatorio e integridad
        self.var_num_registro = tk.StringVar(value="N/A")
        self.var_offset_tell = tk.StringVar(value="0 bytes")
        self.var_tamano_fijo = tk.StringVar(value="120 bytes (definido en modelo)")
        self.var_estado_hash = tk.StringVar(value="Pendiente de verificación")

        self._configurar_estilos()
        self._crear_menu()
        self._crear_layout_principal()
        self._crear_barra_estado()

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        if "vista" in estilo.theme_names():
            estilo.theme_use("vista")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 12, "bold"))
        estilo.configure("DatoTecnico.TLabel", font=("Consolas", 10, "bold"), foreground="#005fb8")

    def _crear_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        # 1. Menú Contactos (funcional)
        menu_contactos = tk.Menu(barra_menu, tearoff=0)
        menu_contactos.add_command(label="Agregar contacto", command=self.on_agregar_contacto, accelerator="Ctrl+N")
        menu_contactos.add_command(label="Buscar por ID", command=self.on_buscar_contacto, accelerator="Ctrl+F")
        menu_contactos.add_command(label="Modificar contacto", command=self.on_modificar_contacto, accelerator="Ctrl+M")
        menu_contactos.add_separator()
        menu_contactos.add_command(label="Limpiar campos", command=self.limpiar_formulario)
        menu_contactos.add_separator()
        menu_contactos.add_command(label="Salir", command=self.quit)
        barra_menu.add_cascade(label="Contactos", menu=menu_contactos)

        # 2. Menú Exportar (funcional)
        menu_exportar = tk.Menu(barra_menu, tearoff=0)
        menu_exportar.add_command(label="Exportar a JSON", command=self.on_exportar_json)
        menu_exportar.add_command(label="Generar reporte PDF", command=self.on_generar_pdf)
        barra_menu.add_cascade(label="Exportar", menu=menu_exportar)

        # 3. Menú Herramientas (funcional)
        menu_herramientas = tk.Menu(barra_menu, tearoff=0)
        menu_herramientas.add_command(label="Verificar integridad (SHA-256)", command=self.on_verificar_integridad)
        menu_herramientas.add_command(label="Crear respaldo ZIP", command=self.on_crear_respaldo_zip)
        menu_herramientas.add_separator()
        menu_herramientas.add_command(label="Información del archivo...", command=self.on_mostrar_info_archivo)
        barra_menu.add_cascade(label="Herramientas", menu=menu_herramientas)

        # 4. Menú Ayuda (simulado)
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Guía de estructura de registro", command=self.on_mostrar_ayuda)
        menu_ayuda.add_command(label="Acerca de...", command=self.on_mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        # Atajos de teclado
        self.bind("<Control-n>", lambda e: self.on_agregar_contacto())
        self.bind("<Control-f>", lambda e: self.on_buscar_contacto())
        self.bind("<Control-m>", lambda e: self.on_modificar_contacto())

    def _crear_layout_principal(self):
        contenedor = ttk.Frame(self)
        contenedor.pack(fill=tk.BOTH, expand=True)
        contenedor.columnconfigure(0, weight=3)
        contenedor.columnconfigure(1, weight=2)
        contenedor.rowconfigure(0, weight=1)

        # Panel Izquierdo: Formulario de Contactos
        frame_form = ttk.LabelFrame(contenedor, text=" Datos del Contacto ", padding=15)
        frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=5)
        frame_form.columnconfigure(1, weight=1)

        # Campo ID + Botón rápido de búsqueda
        ttk.Label(frame_form, text="ID (Entero único):").grid(row=0, column=0, sticky="w", pady=8)
        frame_id = ttk.Frame(frame_form)
        frame_id.grid(row=0, column=1, sticky="ew", pady=8, padx=(10, 0))
        frame_id.columnconfigure(0, weight=1)

        self.entry_id = ttk.Entry(frame_id, textvariable=self.var_id)
        self.entry_id.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(frame_id, text="Buscar ID", command=self.on_buscar_contacto).grid(row=0, column=1)

        # Resto de campos obligatorios
        campos = [
            ("Nombre completo:", self.var_nombre, 1),
            ("Teléfono:", self.var_telefono, 2),
            ("Correo electrónico:", self.var_correo, 3),
            ("Ciudad:", self.var_ciudad, 4),
        ]

        for texto, variable, fila in campos:
            ttk.Label(frame_form, text=texto).grid(row=fila, column=0, sticky="w", pady=8)
            ttk.Entry(frame_form, textvariable=variable).grid(row=fila, column=1, sticky="ew", pady=8, padx=(10, 0))

        # Botonera de acciones directas
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        frame_botones.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(frame_botones, text="Agregar", command=self.on_agregar_contacto).grid(row=0, column=0, sticky="ew", padx=3)
        ttk.Button(frame_botones, text="Modificar en el Lugar", command=self.on_modificar_contacto).grid(row=0, column=1, sticky="ew", padx=3)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_formulario).grid(row=0, column=2, sticky="ew", padx=3)

        # Panel Derecho: Monitor de Acceso Aleatorio y Bitácora
        frame_tecnico = ttk.LabelFrame(contenedor, text=" Monitor de Acceso Aleatorio (seek / tell) ", padding=15)
        frame_tecnico.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=5)
        frame_tecnico.columnconfigure(1, weight=1)
        frame_tecnico.rowconfigure(5, weight=1)

        ttk.Label(frame_tecnico, text="Núm. de Registro:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(frame_tecnico, textvariable=self.var_num_registro, style="DatoTecnico.TLabel").grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frame_tecnico, text="Posición tell():").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(frame_tecnico, textvariable=self.var_offset_tell, style="DatoTecnico.TLabel").grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(frame_tecnico, text="Tamaño Registro:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(frame_tecnico, textvariable=self.var_tamano_fijo).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frame_tecnico, text="Integridad SHA-256:").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Label(frame_tecnico, textvariable=self.var_estado_hash).grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(frame_tecnico, text="Bitácora de operaciones de archivo:").grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 4))

        self.txt_bitacora = tk.Text(frame_tecnico, height=8, width=32, font=("Consolas", 9), state="disabled", bg="#f8f9fa")
        self.txt_bitacora.grid(row=5, column=0, columnspan=2, sticky="nsew")

    def _crear_barra_estado(self):
        self.var_barra_estado = tk.StringVar(value="Listo. Codificación activa: UTF-8.")
        barra = ttk.Label(self, textvariable=self.var_barra_estado, relief=tk.SUNKEN, anchor=tk.W, padding=(6, 3))
        barra.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))


    def registrar_evento(self, mensaje: str):
        self.txt_bitacora.configure(state="normal")
        self.txt_bitacora.insert(tk.END, f"> {mensaje}\n")
        self.txt_bitacora.see(tk.END)
        self.txt_bitacora.configure(state="disabled")
        self.var_barra_estado.set(mensaje)

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_telefono.set("")
        self.var_correo.set("")
        self.var_ciudad.set("")
        self.var_num_registro.set("N/A")
        self.var_offset_tell.set("0 bytes")
        self.entry_id.focus_set()
        self.registrar_evento("Formulario reiniciado.")

    def obtener_datos_formulario(self, validar_todos=True):
        id_str = self.var_id.get().strip()
        if not id_str.isdigit():
            messagebox.showwarning("ID inválido", "El campo ID es obligatorio y debe ser un número entero positivo.")
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

    # --- Eventos del Menú Contactos ---

    def on_agregar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=True)
        if not datos:
            return
        self.registrar_evento(f"[Pendiente] Agregar ID {datos['id']} y actualizar índice JSON.")

    def on_buscar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=False)
        if not datos:
            return
        self.registrar_evento(f"[Pendiente] Buscar ID {datos['id']} en índice primario.")

    def on_modificar_contacto(self):
        datos = self.obtener_datos_formulario(validar_todos=True)
        if not datos:
            return
        self.registrar_evento(f"[Pendiente] Sobrescribir registro del ID {datos['id']} en el lugar.")

    # --- Eventos del Menú Exportar ---

    def on_exportar_json(self):
        self.registrar_evento("[Pendiente] Exportar todos los registros a JSON.")
        messagebox.showinfo("Exportar JSON", "Función lista para conectar con el servicio de exportación.")

    def on_generar_pdf(self):
        # TODO: Conectar con servicio fpdf2 a partir del JSON exportado
        self.registrar_evento("[Pendiente] Generar reporte PDF desde archivo JSON.")
        messagebox.showinfo("Generar PDF", "Función lista para conectar con el generador fpdf2.")

    # --- Eventos del Menú Herramientas ---

    def on_verificar_integridad(self):
        # TODO: Conectar con servicio hashlib SHA-256
        self.registrar_evento("[Pendiente] Recalcular SHA-256 y comparar con archivo hash.")
        messagebox.showinfo("Integridad SHA-256", "Verificación de hash lista para implementar.")

    def on_crear_respaldo_zip(self):
        # TODO: Conectar con zipfile y mostrar tamaño original vs comprimido
        self.registrar_evento("[Pendiente] Comprimir datos e índice en archivo ZIP.")
        messagebox.showinfo("Respaldo ZIP", "Compresión ZIP lista para implementar.")

    def on_mostrar_info_archivo(self):
        ventana_info = tk.Toplevel(self)
        ventana_info.title("Información y Permisos del Archivo")
        ventana_info.geometry("400x230")
        ventana_info.resizable(False, False)
        ventana_info.transient(self)
        ventana_info.grab_set()

        frame = ttk.Frame(ventana_info, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # TODO: Reemplazar valores de prueba con llamadas reales a os.stat() y os.access()
        metadatos = [
            ("Archivo:", "data/contactos.dat"),
            ("Tamaño actual:", "Pendiente (os.stat.st_size)"),
            ("Última modificación:", "Pendiente (os.stat.st_mtime)"),
            ("Permiso de lectura (R_OK):", "Pendiente (os.access)"),
            ("Permiso de escritura (W_OK):", "Pendiente (os.access)"),
        ]

        for i, (etiqueta, valor) in enumerate(metadatos):
            ttk.Label(frame, text=etiqueta, font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            ttk.Label(frame, text=valor).grid(row=i, column=1, sticky="w", padx=(12, 0), pady=5)

        ttk.Button(frame, text="Cerrar", command=ventana_info.destroy).grid(row=len(metadatos), column=0, columnspan=2, pady=(15, 0))

    # --- Eventos del Menú Ayuda (Simulado) ---

    def on_mostrar_ayuda(self):
        mensaje = (
            "Funcionamiento de la Agenda con Acceso Aleatorio:\n\n"
            "1. Cada contacto se almacena en un registro de longitud fija en UTF-8.\n"
            "2. El archivo de índice relaciona cada ID con su número de registro.\n"
            "3. Las búsquedas y ediciones usan seek() y tell() para ir directo al byte exacto."
        )
        messagebox.showinfo("Guía del Sistema", mensaje)

    def on_mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Agenda de Contactos con Acceso Aleatorio\n"
            "Ingeniería en Informática y Sistemas - URL\n"
            "Laboratorio No. 2 - Manejo de Archivos"
        )