import tkinter as tk
from tkinter import ttk, messagebox
import requests
from widgets.input_dialog import InputDialog
from datetime import datetime

class CRUDApp:
    """
    Clase para la aplicación CRUD que maneja múltiples bases de datos.

    Atributos:
        API_URL (str): URL base de la API.
        root (tk.Tk): Ventana principal de la aplicación.
        style (ttk.Style): Estilo de la aplicación.
        main_container (ttk.Frame): Contenedor principal de la aplicación.
        filter_var (tk.StringVar): Variable para el filtro de búsqueda.
        current_page (int): Página actual de la paginación.
        total_pages (int): Total de páginas disponibles.
        has_next (bool): Indica si hay una página siguiente.
        has_prev (bool): Indica si hay una página anterior.
        notebook (ttk.Notebook): Contenedor de pestañas para las bases de datos.
        current_view (dict): Diccionario para almacenar la vista actual de cada pestaña.
        current_theme (str): Tema actual de la aplicación.
    """

    def __init__(self):
        """
        Inicializa la clase CRUDApp y configura la interfaz de usuario.
        """
        self.API_URL = "http://localhost:5000/api"

        # Crear ventana principal con tema
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Amaluz")
        self.root.geometry("800x600")
        self.root.minsize(800, 700)
        self.root.option_add("*tearOff", False)

        # Configurar estilo y tema
        self.style = ttk.Style(self.root)
        self.root.tk.call('source', 'forest-dark.tcl')
        self.root.tk.call('source', 'forest-light.tcl')
        self.style.theme_use('forest-light')

        # Configurar estilos específicos
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('TNotebook', padding=2)
        self.style.configure('TNotebook.Tab', padding=[12, 0])

        # Crear contenedor principal con padding
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill='both', expand=True)

        # Crear un marco para el título y el botón de tema
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', padx=5, pady=5)

        # Añadir etiqueta de título
        title_label = ttk.Label(header_frame, text="Sistema de Gestión Amaluz", font=("Helvetica", 16, "bold"))
        title_label.pack(side='left', padx=5, pady=5)

        # Añadir botón de cambio de tema
        theme_button = ttk.Button(header_frame, text="Cambiar Tema", style="Accent.TButton", command=self.toggle_theme)
        theme_button.pack(side='right', padx=5, pady=5)

        # Inicializar variable de filtro
        self.filter_var = tk.StringVar()

        # Inicializar variables de paginación
        self.current_page = 1
        self.total_pages = 1
        self.has_next = False
        self.has_prev = False

        # Crear notebook para las pestañas de bases de datos
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Añadir evento de cambio de pestaña
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Inicializar diccionario current_view antes de crear las pestañas
        self.current_view = {
            'amaluz': None,
            'current_tree': None,
            'current_endpoint': None,
            'current_config': None
        }

        # Inicializar pestañas de bases de datos
        self.create_amaluz_tab()

        # Establecer tema inicial
        self.current_theme = 'forest-light'

    def toggle_theme(self):
        """
        Alterna el tema de la aplicación entre 'forest-light' y 'forest-dark'.
        """
        if self.current_theme == 'forest-light':
            self.style.theme_use('forest-dark')
            self.current_theme = 'forest-dark'
        else:
            self.style.theme_use('forest-light')
            self.current_theme = 'forest-light'

    def on_tab_changed(self, event):
        """
        Maneja los eventos de cambio de pestaña.

        Args:
            event: El evento de cambio de pestaña.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if tab_view and tab_view['table'].get() != "Seleccione una tabla":
            tables_config = self.get_tables_config(tab_name)
            selected_table = tab_view['table'].get()
            current_config = tables_config.get(selected_table)

            if current_config:
                # Actualiza la vista actual con la configuración de la pestaña

                self.current_view['current_tree'] = tab_view['tree']
                self.current_view['current_endpoint'] = current_config['endpoint']
                self.current_view['current_config'] = current_config
                self.current_page = 1

                # Actualiza el selector de tamaño de página para que coincida con el tamaño de página de la pestaña actual
                current_page_size = str(tab_view['pagination']['page_size'])
                tab_view['pagination']['page_size_selector'].set(current_page_size)

                # Fuerza la actualización de la paginación antes de cargar los datos
                self.has_next = False
                self.has_prev = False
                self.total_pages = 1
                self.update_pagination_controls()

                # Carga los datos y actualiza la paginación
                if self.load_data(
                        tab_view['tree'],
                        current_config['endpoint'],
                        self.current_page,
                        tab_view['pagination']['page_size']
                ):
                    self.update_pagination_controls()

    def get_tables_config(self, tab_name):
        """
       Devuelve la configuración de las tablas para el nombre de pestaña dado.

       Args:
           tab_name (str): Nombre de la pestaña.

       Returns:
           dict: Configuración de las tablas para la pestaña especificada.
       """
        tables_config = {
            'amaluz': {
                'Empleados': {
                    'endpoint': 'amaluz/empleados', 'columns': [
                        ('id_empleado', 'ID Empleado', 50),
                        ('nombre', 'Nombre', 150),
                        ('correo', 'Correo Electrónico', 200),
                        ('telefono', 'Teléfono', 100),
                        ('fecha_nacimiento', 'Fecha de Nacimiento', 120),
                        ('genero', 'Género', 80),
                        ('tipo_usuario', 'Tipo de Usuario', 120),
                        ('estado', 'Estado', 80),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                },
                'Proveedores': {
                    'endpoint': 'amaluz/proveedores', 'columns': [
                        ('id_proveedor', 'ID Proveedor', 50),
                        ('nombre', 'Nombre', 150),
                        ('descripcion', 'Descripción', 200),
                        ('telefono', 'Teléfono', 100),
                        ('direccion', 'Dirección', 200),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                },
                'Productos': {
                    'endpoint': 'amaluz/productos', 'columns': [
                        ('id_producto', 'ID Producto', 50),
                        ('nombre', 'Nombre', 150),
                        ('precio_venta', 'Precio de Venta', 100),
                        ('categoria', 'Categoría', 150),
                        ('fragancia', 'Fragancia', 150),
                        ('periodo_garantia', 'Período de Garantía', 100),
                        ('id_proveedor', 'ID Proveedor', 50),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                },
                'Clientes': {
                    'endpoint': 'amaluz/clientes', 'columns': [
                        ('id_cliente', 'ID Cliente', 50),
                        ('nombre', 'Nombre', 150),
                        ('telefono', 'Teléfono', 100),
                        ('correo', 'Correo Electrónico', 200),
                        ('genero', 'Género', 80),
                        ('fecha_nacimiento', 'Fecha de Nacimiento', 120),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                },
                'Pedidos': {
                    'endpoint': 'amaluz/pedidos', 'columns': [
                        ('id_pedido', 'ID Pedido', 50),
                        ('id_cliente', 'ID Cliente', 50),
                        ('metodo_pago', 'Método de Pago', 150),
                        ('costo_total', 'Costo Total', 100),
                        ('estado', 'Estado', 100),
                        ('fecha_pedido', 'Fecha de Pedido', 150)
                    ]
                },
                'Detalle Pedidos': {
                    'endpoint': 'amaluz/detalle-pedidos', 'columns': [
                        ('id_detalle', 'ID Detalle', 50),
                        ('id_pedido', 'ID Pedido', 50),
                        ('id_producto', 'ID Producto', 50),
                        ('cantidad', 'Cantidad', 80),
                        ('precio_unitario', 'Precio Unitario', 100),
                        ('subtotal', 'Subtotal', 100),
                        ('fecha_venta', 'Fecha de Venta', 150)
                    ]
                },
                'Envíos': {
                    'endpoint': 'amaluz/envios', 'columns': [
                        ('id_envio', 'ID Envío', 50),
                        ('id_pedido', 'ID Pedido', 50),
                        ('empresa_envio', 'Empresa de Envío', 150),
                        ('referencia_emp_envio', 'Referencia', 100),
                        ('costo_envio', 'Costo de Envío', 100),
                        ('direccion', 'Dirección', 200),
                        ('ciudad', 'Ciudad', 100),
                        ('departamento', 'Departamento', 100),
                        ('estado_envio', 'Estado', 100),
                        ('fecha_envio', 'Fecha de Envío', 150),
                        ('fecha_estimada_entrega', 'Entrega Estimada', 150),
                        ('fecha_entrega_real', 'Entrega Real', 150)
                    ]
                },
                'Calificaciones': {
                    'endpoint': 'amaluz/calificaciones', 'columns': [
                        ('id_calificacion', 'ID Calificación', 50),
                        ('id_cliente', 'ID Cliente', 50),
                        ('id_producto', 'ID Producto', 50),
                        ('calificacion', 'Calificación', 80),
                        ('fecha_calificacion', 'Fecha', 150)
                    ]
                },
                'Inventario': {
                    'endpoint': 'amaluz/inventario', 'columns': [
                        ('id_inventario', 'ID Inventario', 50),
                        ('id_producto', 'ID Producto', 50),
                        ('cantidad_total', 'Cantidad Total', 100),
                        ('cantidad_disponible', 'Cantidad Disponible', 100),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                },
                'Auditoría Inventario': {
                    'endpoint': 'amaluz/auditoria-inventario', 'columns': [
                        ('id', 'ID', 50),
                        ('id_producto', 'ID Producto', 50),
                        ('cantidad_anterior', 'Cantidad Anterior', 100),
                        ('cantidad_nueva', 'Cantidad Nueva', 100),
                        ('fecha_registro', 'Fecha de Registro', 150)
                    ]
                }
            }
        }
        return tables_config.get(tab_name, {})

    def refresh_data(self):
        """
        Actualiza los datos en la tabla actual.
        """
        tree = self.current_view['current_tree']
        config = self.current_view['current_config']
        if tree and config:
            current_tab = self.notebook.select()
            tab_index = self.notebook.index(current_tab)
            tab_name = ['amaluz'][tab_index]

            tab_view = self.current_view.get(tab_name)
            if not tab_view:
                return

            page_size = tab_view['pagination']['page_size']
            original_bg = self.style.lookup('Treeview', 'background')
            self.style.configure('Success.Treeview', background='#e6ffe6')
            tree.configure(style='Success.Treeview')
            self.load_data(tree, config['endpoint'], self.current_page, page_size)
            tree.after(1000, lambda: [
                self.style.configure('Success.Treeview', background=original_bg),
                tree.configure(style='Treeview')
            ])

    def add_record(self):
        """
        Abre un cuadro de diálogo para agregar un nuevo registro.
        """
        tree = self.current_view['current_tree']
        config = self.current_view['current_config']
        if not config:
            return

        fields = [(col[0], col[1]) for col in config['columns'] if col[0] != 'id']
        dialog = InputDialog(self.root, "Agregar Registro", fields)

        if dialog.result:
            try:
                response = requests.post(
                    f"{self.API_URL}/{config['endpoint']}",
                    json=dialog.result
                )
                if response.status_code == 201:
                    messagebox.showinfo("Éxito", "Registro agregado correctamente")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "No se pudo agregar el registro")
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar el registro: {str(e)}")

    def edit_record(self):
        """
        Abre un cuadro de diálogo para editar el registro seleccionado.
        """
        tree = self.current_view['current_tree']
        config = self.current_view['current_config']
        if not config:
            return

        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro")
            return

        values = tree.item(selected_item)['values']
        fields = [(col[0], col[1]) for col in config['columns'] if col[0] != 'id']
        edit_values = list(values[1:])  # Convertir valores a lista para modificación

        # Formatear fechas para campos que contienen 'fecha' en su nombre
        edit_values = self.format_dates_for_edit(fields, edit_values)

        dialog = InputDialog(self.root, "Editar Registro", fields, edit_values)

        if dialog.result:
            try:
                record_id = values[1]
                response = requests.put(
                    f"{self.API_URL}/{config['endpoint']}/{record_id}",
                    json=dialog.result
                )
                if response.status_code == 200:
                    messagebox.showinfo("Éxito", "Registro actualizado correctamente")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el registro")
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar el registro: {str(e)}")

    def delete_record(self):
        """
        Elimina los registros marcados con casillas de verificación.

        Verifica los elementos seleccionados en el Treeview y los elimina
        mediante solicitudes a la API.

        Muestra mensajes de advertencia, confirmación y error según sea necesario.
        """
        tree = self.current_view['current_tree']
        config = self.current_view['current_config']
        if not config:
            return

        all_items = tree.get_children()
        checked_items = [item for item in all_items
                         if tree.item(item)['values']
                         and tree.item(item)['values'][0] == "☑"]

        if not checked_items:
            messagebox.showwarning("Advertencia", "Por favor seleccione al menos un registro")
            return

        num_items = len(checked_items)
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar {num_items} registro{'s' if num_items > 1 else ''}?"):
            try:
                success_count = 0
                error_count = 0
                for item in checked_items:
                    record_id = tree.item(item)['values'][1]
                    response = requests.delete(f"{self.API_URL}/{config['endpoint']}/{record_id}")
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1

                if success_count > 0:
                    messagebox.showinfo("Éxito",
                                        f"Se eliminaron {success_count} registro{'s' if success_count > 1 else ''} correctamente"
                                        + (f"\nNo se pudieron eliminar {error_count} registros" if error_count > 0 else ""))
                else:
                    messagebox.showerror("Error", "No se pudo eliminar ningún registro")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar registros: {str(e)}")

    def configure_tree(self, tree, columns):
        """
        Configura las columnas del Treeview con una columna de casillas de verificación.

        Args:
            tree (ttk.Treeview): El widget Treeview a configurar.
            columns (list): Lista de columnas a configurar en el Treeview.
        """
        tree.delete(*tree.get_children())

        all_columns = ["checkbox"] + [col[0] for col in columns]
        tree["columns"] = all_columns

        tree.column("checkbox", width=50, anchor="center")
        tree.heading("checkbox", text="✓")

        for col_id, col_name, width in columns:
            tree.column(col_id, width=width, minwidth=width)
            tree.heading(col_id, text=col_name, command=lambda _col=col_id: self.sort_column(tree, _col, False))

        tree.bind("<Button-1>", lambda e: self.on_checkbox_click(e, tree))
        tree.bind("<space>", lambda e: self.on_checkbox_click(e, tree))

    def sort_column(self, tree, col, reverse):
        """
        Ordena los datos de la columna del Treeview por tipo.

        Args:
            tree (ttk.Treeview): El widget Treeview a ordenar.
            col (str): La columna a ordenar.
            reverse (bool): Indica si la ordenación debe ser en orden inverso.
        """
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        if data:
            try:
                [int(item[0]) for item in data]
                data.sort(key=lambda x: int(x[0]) if x[0].strip() else 0, reverse=reverse)
            except ValueError:
                try:
                    [float(item[0]) for item in data]
                    data.sort(key=lambda x: float(x[0]) if x[0].strip() else 0.0, reverse=reverse)
                except ValueError:
                    data.sort(key=lambda x: x[0].lower() if x[0].strip() else "", reverse=reverse)

        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)

        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

    def create_tab_layout(self, tab_frame, tables_config):
        """
        Crea un diseño consistente para cada pestaña de la base de datos.

        Args:
            tab_frame (ttk.Frame): El marco de la pestaña donde se creará el diseño.
            tables_config (dict): Configuración de las tablas para la pestaña.
        """
        selector_frame = ttk.LabelFrame(tab_frame, text="Seleccionar Tabla", padding="10")
        selector_frame.pack(fill='x', padx=5, pady=5)

        table_selector = ttk.Combobox(selector_frame, values=list(tables_config.keys()), state='readonly')
        table_selector.pack(side='left', padx=5)
        table_selector.set("Seleccione una tabla")

        buttons_frame = ttk.Frame(selector_frame)
        buttons_frame.pack(side='right')

        crud_buttons = [
            ("Agregar", self.add_record, 'CreateButton'),
            ("Editar", self.edit_record, 'UpdateButton'),
            ("Eliminar", self.delete_record, "DeleteButton"),
            ("↻", self.refresh_data, "RefreshButton")
        ]

        for text, command, style in crud_buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, style=style, width=3 if text == "↻" else None)
            btn.pack(side='left', padx=2)

        filter_frame = ttk.LabelFrame(tab_frame, text="Filtrar", padding="10")
        filter_frame.pack(fill='x', padx=5, pady=5)

        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        filter_entry.pack(side='left', padx=5)

        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.pack(side='left')

        filter_button = ttk.Button(filter_buttons_frame, text="Aplicar Filtro", style="FilterButton",
                                   command=lambda: self.apply_filter(tables_config[table_selector.get()]))
        filter_button.pack(side='left', padx=2)

        clear_filter_button = ttk.Button(filter_buttons_frame, text="Limpiar Filtro", style="ClearFilterButton",
                                         command=lambda: self.clear_filter(tables_config[table_selector.get()]))
        clear_filter_button.pack(side='left', padx=2)

        content_frame = ttk.Frame(tab_frame)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tree_frame = ttk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)

        y_scroll = ttk.Scrollbar(tree_frame)
        y_scroll.pack(side='right', fill='y')

        x_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scroll.pack(side='bottom', fill='x')

        tree = ttk.Treeview(tree_frame, selectmode='browse', show='headings',
                            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.pack(fill='both', expand=True)

        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)

        table_selector.bind('<<ComboboxSelected>>',
                            lambda e: self.on_table_selected(table_selector.get(), tree, tables_config))

        pagination_frame = ttk.Frame(tab_frame)
        pagination_frame.pack(fill='x', padx=5, pady=5)

        page_size_frame = ttk.Frame(pagination_frame)
        page_size_frame.pack(side='left', padx=5)

        ttk.Label(page_size_frame, text="Registros por página:").pack(side='left', padx=2)
        page_size_selector = ttk.Combobox(page_size_frame, values=['10', '25', '50', '100'],
                                          width=5, state='readonly')
        page_size_selector.set('10')
        page_size_selector.pack(side='left', padx=2)

        page_size_selector.bind('<<ComboboxSelected>>',
                                lambda e: self.on_page_size_changed(e, tables_config))

        nav_frame = ttk.Frame(pagination_frame)
        nav_frame.pack(side='right', padx=5)

        prev_button = ttk.Button(nav_frame, text="Anterior", style="PreviousButton",
                                 command=lambda: self.prev_page(tables_config))
        prev_button.pack(side='left', padx=5)

        page_label = ttk.Label(nav_frame, text="Página 1 de 1")
        page_label.pack(side='left', padx=5)

        next_button = ttk.Button(nav_frame, text="Siguiente", style="NextButton",
                                 command=lambda: self.next_page(tables_config))
        next_button.pack(side='left', padx=5)

        pagination_controls = {
            'prev_button': prev_button,
            'page_label': page_label,
            'next_button': next_button,
            'page_size_selector': page_size_selector,
            'current_page': 1,
            'total_pages': 1,
            'has_next': False,
            'has_prev': False,
            'page_size': 10
        }

        prev_button.config(state='disabled')
        next_button.config(state='disabled')

        return tree, table_selector, pagination_controls

    def apply_filter(self, config):
        """
        Aplica un filtro a los datos del Treeview.

        Args:
            config (dict): Configuración de la tabla seleccionada.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view:
            return

        filter_text = self.filter_var.get().strip().lower()
        page_size = tab_view['pagination']['page_size']

        try:
            response = requests.get(
                f"{self.API_URL}/{config['endpoint']}",
                params={'page': 1, 'page_size': page_size, 'filter': filter_text}
            )
            if response.status_code == 200:
                data = response.json()
                self.current_page = data['pagination']['page']
                self.total_pages = data['pagination']['total_pages']
                self.has_next = data['pagination']['has_next']
                self.has_prev = data['pagination']['has_prev']
                tree = self.current_view['current_tree']
                tree.delete(*tree.get_children())
                for item in data['data']:
                    values = ['☐']
                    for col in config['columns']:
                        value = item.get(col[0], '')
                        # Formatear fechas a DD/MM/YYYY
                        if isinstance(value, str) and ('fecha' in col[0].lower()):
                            value = self.format_date(value)
                        values.append(str(value))
                    tree.insert('', 'end', values=values)

                self.update_pagination_controls()
            else:
                messagebox.showerror("Error", "Error al aplicar el filtro")
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")

    def clear_filter(self, config):
        """
        Limpia el filtro y actualiza la vista de la tabla.

        Args:
            config (dict): Configuración de la tabla seleccionada.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view:
            return

        self.filter_var.set('')
        self.current_page = 1
        self.load_data(
            self.current_view['current_tree'],
            config['endpoint'],
            self.current_page,
            tab_view['pagination']['page_size']
        )

    def create_amaluz_tab(self):
        """
        Crea la pestaña para la base de datos Amaluz con su selector de tabla y contenido.
        """
        amaluz_frame = ttk.Frame(self.notebook)
        self.notebook.add(amaluz_frame, text="Amaluz")

        tables_config = self.get_tables_config('amaluz')
        tree, selector, pagination = self.create_tab_layout(amaluz_frame, tables_config)
        self.current_view['amaluz'] = {'table': selector, 'tree': tree, 'pagination': pagination}

    def on_table_selected(self, table_name, tree, tables_config):
        """
        Maneja los cambios de selección de tabla.

        Args:
            table_name (str): Nombre de la tabla seleccionada.
            tree (ttk.Treeview): El widget Treeview a configurar.
            tables_config (dict): Configuración de las tablas.
        """
        if table_name in tables_config:
            config = tables_config[table_name]
            self.filter_var.set('')
            self.configure_tree(tree, config['columns'])
            self.current_view['current_tree'] = tree
            self.current_view['current_endpoint'] = config['endpoint']
            self.current_view['current_config'] = config

            current_tab = self.notebook.select()
            tab_index = self.notebook.index(current_tab)
            tab_name = ['amaluz'][tab_index]

            tab_view = self.current_view.get(tab_name)
            if not tab_view or 'pagination' not in tab_view:
                return

            page_size = tab_view['pagination']['page_size']
            tab_view['pagination']['page_size_selector'].set(str(page_size))

            self.current_page = 1

            self.has_next = False
            self.has_prev = False
            self.total_pages = 1
            self.update_pagination_controls()

            if self.load_data(tree, config['endpoint'], self.current_page, page_size):
                self.update_pagination_controls()

    def on_checkbox_click(self, event, tree):
        """
        Maneja los clics en las casillas de verificación.

        Args:
            event: El evento de clic.
            tree (ttk.Treeview): El widget Treeview a actualizar.
        """
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            if column == "#1":  # Checkbox column
                item = tree.identify_row(event.y)
                if item:
                    current_values = tree.item(item)['values']
                    if current_values:
                        tree.item(item, values=["☑" if current_values[0] != "☑" else "☐"] + current_values[1:])
                        if current_values[0] != "☑":
                            tree.selection_add(item)
                        else:
                            tree.selection_remove(item)

    def load_data(self, tree, endpoint, page=1, page_size=10):
        """
        Carga los datos en el Treeview desde el endpoint especificado.

        Args:
            tree (ttk.Treeview): El widget Treeview donde se cargarán los datos.
            endpoint (str): El endpoint de la API desde donde se obtendrán los datos.
            page (int, opcional): El número de página a cargar. Por defecto es 1.
            page_size (int, opcional): El tamaño de la página. Por defecto es 10.

        Returns:
            bool: True si los datos se cargaron correctamente, False en caso contrario.
        """
        try:
            params = {
                'page': page,
                'page_size': page_size
            }
            if self.filter_var.get().strip():
                params['filter'] = self.filter_var.get().strip()

            response = requests.get(f"{self.API_URL}/{endpoint}", params=params)
            if response.status_code == 200:
                data = response.json()
                pagination = data.get('pagination', {})
                # Actualizar el estado de la paginación
                self.current_page = pagination.get('page', 1)
                self.total_pages = pagination.get('total_pages', 1)
                self.has_next = pagination.get('has_next', False)
                self.has_prev = pagination.get('has_prev', False)
                # Limpiar y actualizar el Treeview
                tree.delete(*tree.get_children())
                for item in data.get('data', []):
                    values = ['☐']
                    for col in self.current_view['current_config']['columns']:
                        value = item.get(col[0], '')
                        # Formatear fechas a DD/MM/YYYY
                        if isinstance(value, str) and ('fecha' in col[0].lower()):
                            value = self.format_date(value)
                        values.append(str(value))
                    tree.insert('', 'end', values=values)

                # Actualizar los controles de paginación después de cargar los datos
                self.root.after(100, self.update_pagination_controls)
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            return False

    def format_date(self, date_val):
        """
        Formatea cadenas de fecha a DD/MM/YYYY.

        Args:
            date_val (str): La cadena de fecha a formatear.

        Returns:
            str: La fecha formateada en DD/MM/YYYY.
        """
        try:
            # Convertir a cadena si la entrada no es ya una cadena
            date_str = str(date_val)

            if 'GMT' in date_str:
                date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
            elif 'T' in date_str:
                date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            elif '/' in date_str:
                date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            return date_val

    def format_dates_for_edit(self, fields, values):
        """
        Formatea las fechas para la edición en el cuadro de diálogo de entrada.

        Args:
            fields (list): Lista de campos de la tabla.
            values (list): Lista de valores de la tabla.

        Returns:
            list: Lista de valores con las fechas formateadas.
        """
        for i, (field_name, _) in enumerate(fields):
            if 'fecha' in field_name.lower() and values[i]:
                values[i] = self.format_date(values[i])
        return values

    def update_pagination_controls(self):
        """
        Actualiza los controles de paginación según el estado actual.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view or 'pagination' not in tab_view:
            return

        pagination = tab_view['pagination']

        pagination['current_page'] = max(1, self.current_page)
        pagination['total_pages'] = max(1, self.total_pages)
        pagination['has_next'] = self.has_next
        pagination['has_prev'] = self.has_prev

        pagination['page_label'].config(
            text=f"Página {pagination['current_page']} de {pagination['total_pages']}"
        )

        pagination['prev_button'].config(
            state='normal' if pagination['has_prev'] else 'disabled'
        )
        pagination['next_button'].config(
            state='normal' if pagination['has_next'] else 'disabled'
        )

        self.root.update_idletasks()

    def next_page(self, tables_config):
        """
        Avanza a la siguiente página de datos en la tabla actual.

        Args:
            tables_config (dict): Configuración de las tablas.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view:
            return

        pagination = tab_view['pagination']
        if pagination['has_next']:
            pagination['current_page'] += 1
            self.current_page = pagination['current_page']
            self.load_data(
                tab_view['tree'],
                self.current_view['current_endpoint'],
                self.current_page,
                pagination['page_size']
            )

    def prev_page(self, tables_config):
        """
        Retrocede a la página anterior de datos en la tabla actual.

        Args:
            tables_config (dict): Configuración de las tablas.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view:
            return

        pagination = tab_view['pagination']
        if pagination['has_prev']:
            pagination['current_page'] -= 1
            self.current_page = pagination['current_page']
            self.load_data(
                tab_view['tree'],
                self.current_view['current_endpoint'],
                self.current_page,
                pagination['page_size']
            )

    def on_page_size_changed(self, event, tables_config):
        """
        Maneja los cambios en el tamaño de la página.

        Args:
            event: El evento de cambio de tamaño de página.
            tables_config (dict): Configuración de las tablas.
        """
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        tab_name = ['amaluz'][tab_index]

        tab_view = self.current_view.get(tab_name)
        if not tab_view or not tab_view.get('pagination'):
            return

        new_size = int(tab_view['pagination']['page_size_selector'].get())
        tab_view['pagination']['page_size'] = new_size

        self.current_page = 1
        tab_view['pagination']['current_page'] = 1

        if self.current_view.get('current_endpoint'):
            self.load_data(
                tab_view['tree'],
                self.current_view['current_endpoint'],
                page=1,
                page_size=new_size
            )

# Inicializar la aplicación
if __name__ == '__main__':
    app = CRUDApp()
    app.root.mainloop()