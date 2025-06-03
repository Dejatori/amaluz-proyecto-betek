from app.models import db
from sqlalchemy.orm import validates


class Empleado(db.Model):
    """
    Modelo que representa a un empleado.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_empleado (int): Identificador único del empleado.
        nombre (str): Nombre del empleado.
        correo (str): Correo electrónico del empleado.
        contraseña (str): Contraseña del empleado.
        telefono (str): Número de teléfono del empleado.
        fecha_nacimiento (date): Fecha de nacimiento del empleado en formato 'YYYY-MM-DD'.
        genero (enum): Género del empleado, debe ser uno de los valores definidos en `GeneroEmpleadoEnum`.
        tipo_usuario (enum): Tipo de usuario del empleado, debe ser uno de los valores definidos en `TipoUsuarioEnum`.
        estado (enum): Estado del empleado, debe ser uno de los valores definidos en `EstadoEmpleadoEnum`.
        fecha_registro (datetime): Fecha y hora de registro del empleado, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'empleado'

    id_empleado = db.Column('id_empleado', db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column('nombre', db.String(255), nullable=False)
    correo = db.Column('correo', db.String(255), unique=True, nullable=False)
    contraseña = db.Column('contraseña', db.String(255), nullable=False)
    telefono = db.Column('telefono', db.String(20), nullable=True)
    fecha_nacimiento = db.Column('fecha_nacimiento', db.Date, nullable=True)
    genero = db.Column('genero', db.Enum('masculino', 'femenino', 'otro', name='genero_empleado'), nullable=False)
    tipo_usuario = db.Column('tipo_usuario',
                             db.Enum('propietario', 'administrador', 'empleado', name='tipo_usuario_empleado'),
                             nullable=False)
    estado = db.Column('estado', db.Enum('activo', 'inactivo', 'eliminado', name='estado_empleado'), nullable=False,
                       default='activo')
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('correo')
    def validate_correo(self, key, correo):
        """
        Valida que el correo electrónico tenga un formato correcto.

        Args:
            key (str): Nombre del campo.
            correo (str): Correo electrónico a validar.

        Returns:
            str: Correo electrónico validado.
        """
        if '@' not in correo or '.' not in correo.split('@')[-1]:
            raise ValueError("El correo electrónico debe tener un formato válido.")
        return correo

    @validates('contraseña')
    def validate_contraseña(self, key, contraseña):
        """
        Valida que la contraseña tenga al menos 8 caracteres.

        Args:
            key (str): Nombre del campo.
            contraseña (str): Contraseña a validar.

        Returns:
            str: Contraseña validada.
        """
        if len(contraseña) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return contraseña

    @validates('telefono')
    def validate_telefono(self, key, telefono):
        """
        Valida que el teléfono tenga un máximo de 15 caracteres.

        Args:
            key (str): Nombre del campo.
            telefono (str): Valor del teléfono a validar.

        Returns:
            str: Teléfono validado.

        Raises:
            AssertionError: Si el teléfono tiene más de 15 caracteres.
        """
        assert len(telefono) <= 15, "El teléfono debe tener máximo 15 caracteres"
        return telefono


class Proveedor(db.Model):
    """
    Modelo que representa a un proveedor.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_proveedor (int): Identificador único del proveedor.
        nombre (str): Nombre del proveedor.
        descripcion (text): Descripción del proveedor.
        telefono (str): Número de teléfono del proveedor.
        direccion (str): Dirección del proveedor.
        fecha_registro (datetime): Fecha y hora de registro del proveedor, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'proveedor'

    id_proveedor = db.Column('id_proveedor', db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column('nombre', db.String(255), nullable=False)
    descripcion = db.Column('descripcion', db.Text, nullable=True)
    telefono = db.Column('telefono', db.String(20), nullable=True)
    direccion = db.Column('direccion', db.String(255), nullable=True)
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('telefono')
    def validate_telefono(self, key, telefono):
        """
        Valida que el teléfono tenga un máximo de 15 caracteres.

        Args:
            key (str): Nombre del campo.
            telefono (str): Valor del teléfono a validar.

        Returns:
            str: Teléfono validado.

        Raises:
            AssertionError: Si el teléfono tiene más de 15 caracteres.
        """
        assert len(telefono) <= 15, "El teléfono debe tener máximo 15 caracteres"
        return telefono


class Producto(db.Model):
    """
    Modelo que representa a un producto.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_producto (int): Identificador único del producto.
        nombre (str): Nombre del producto.
        precio_venta (decimal): Precio de venta del producto.
        categoria (enum): Categoría del producto, debe ser uno de los valores definidos en `CategoriaProductoEnum`.
        fragancia (enum): Fragancia del producto, debe ser uno de los valores definidos en `FraganciaProductoEnum`.
        periodo_garantia (int): Periodo de garantía del producto en días.
        id_proveedor (int): Identificador del proveedor del producto, debe ser una clave foránea que referencia a `Proveedor`.
        fecha_registro (datetime): Fecha y hora de registro del producto, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'producto'

    id_producto = db.Column('id_producto', db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column('nombre', db.String(255), nullable=False)
    precio_venta = db.Column('precio_venta', db.Numeric(10, 2), nullable=False)
    categoria = db.Column('categoria',
                          db.Enum('Velas Aromáticas', 'Velas Decorativas', 'Velas Artesanales', 'Velas Personalizadas',
                                  'Velas de Recordatorio', name='categoria_producto'),
                          nullable=False)
    fragancia = db.Column('fragancia',
                          db.Enum('Lavanda', 'Rosa', 'Cítricos', 'Vainilla', 'Chocolate', 'Eucalipto', 'Menta',
                                  'Canela', 'Café', 'Tropical', 'Jazmín', 'Bebé', 'Sándalo', 'Pino', 'Naturaleza',
                                  'Sofe', 'Cítricos Frescos', 'Frutos Rojos', 'Frutos Amarillos', 'Romero', 'Especias',
                                  'Chicle', 'Coco', 'Tabaco & Chanelle', name='fragancia_producto'),
                          nullable=False)
    periodo_garantia = db.Column('periodo_garantia', db.Integer, nullable=False, default=90)
    id_proveedor = db.Column('id_proveedor', db.Integer, db.ForeignKey('proveedor.id_proveedor'), nullable=False)
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)


class Cliente(db.Model):
    """
    Modelo que representa a un cliente.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_cliente (int): Identificador único del cliente.
        nombre (str): Nombre del cliente.
        telefono (str): Número de teléfono del cliente.
        correo (str): Correo electrónico del cliente.
        genero (enum): Género del cliente, debe ser uno de los valores definidos en `GeneroClienteEnum`.
        fecha_nacimiento (date): Fecha de nacimiento del cliente en formato 'YYYY-MM-DD'.
        fecha_registro (datetime): Fecha y hora de registro del cliente, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'cliente'

    id_cliente = db.Column('id_cliente', db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column('nombre', db.String(255), nullable=False)
    telefono = db.Column('telefono', db.String(20), nullable=True)
    correo = db.Column('correo', db.String(255), unique=True, nullable=False)
    genero = db.Column('genero', db.Enum('masculino', 'femenino', 'otro', name='genero_cliente'), nullable=False)
    fecha_nacimiento = db.Column('fecha_nacimiento', db.Date, nullable=True)
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('correo')
    def validate_correo(self, key, correo):
        """
        Valida que el correo electrónico tenga un formato correcto.

        Args:
            key (str): Nombre del campo.
            correo (str): Correo electrónico a validar.

        Returns:
            str: Correo electrónico validado.
        """
        if '@' not in correo or '.' not in correo.split('@')[-1]:
            raise ValueError("El correo electrónico debe tener un formato válido.")
        return correo


class Pedido(db.Model):
    """
    Modelo que representa un pedido realizado por un cliente.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_pedido (int): Identificador único del pedido.
        id_cliente (int): Identificador del cliente que realizó el pedido, debe ser una clave foránea que referencia a `Cliente`.
        metodo_pago (enum): Método de pago utilizado para el pedido, debe ser uno de los valores definidos en `MetodoPagoEnum`.
        costo_total (decimal): Costo total del pedido.
        estado (enum): Estado del pedido, debe ser uno de los valores definidos en `EstadoPedidoEnum`.
        fecha_pedido (datetime): Fecha y hora en que se realizó el pedido, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'pedido'

    id_pedido = db.Column('id_pedido', db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column('id_cliente', db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    metodo_pago = db.Column('metodo_pago',
                            db.Enum('Tarjeta de Crédito', 'Transferencia Bancaria', 'PSE', name='metodo_pago'),
                            nullable=False)
    costo_total = db.Column('costo_total', db.Numeric(10, 2), nullable=False)
    estado = db.Column('estado', db.Enum('pendiente', 'procesando', 'enviado', 'entregado', 'cancelado', 'reembolsado',
                                         name='estado_pedido'), nullable=False, default='pendiente')
    fecha_pedido = db.Column('fecha_pedido', db.DateTime, server_default=db.func.now(), nullable=False)


class DetallePedido(db.Model):
    """
    Modelo que representa los detalles de un pedido.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_detalle (int): Identificador único del detalle del pedido.
        id_pedido (int): Identificador del pedido al que pertenece el detalle, debe ser una clave foránea que referencia a `Pedido`.
        id_producto (int): Identificador del producto incluido en el detalle, debe ser una clave foránea que referencia a `Producto`.
        cantidad (int): Cantidad del producto en el detalle del pedido.
        precio_unitario (decimal): Precio unitario del producto en el momento de la compra.
        subtotal (decimal): Subtotal calculado como cantidad * precio_unitario.
        fecha_venta (datetime): Fecha y hora en que se registró el detalle del pedido, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'detalle_pedido'

    id_detalle = db.Column('id_detalle', db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column('id_pedido', db.Integer, db.ForeignKey('pedido.id_pedido'), nullable=False)
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db.Column('cantidad', db.Integer, nullable=False)
    precio_unitario = db.Column('precio_unitario', db.Numeric(10, 2), nullable=False)
    subtotal = db.Column('subtotal', db.Numeric(10, 2), nullable=False)
    fecha_venta = db.Column('fecha_venta', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('cantidad')
    def validate_cantidad(self, key, cantidad):
        """
        Valida que la cantidad sea un número positivo.

        Args:
            key (str): Nombre del campo.
            cantidad (int): Cantidad a validar.

        Returns:
            int: Cantidad validada.

        Raises:
            ValueError: Si la cantidad es menor o igual a cero.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        return cantidad


class Envio(db.Model):
    """
    Modelo que representa un envío asociado a un pedido.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_envio (int): Identificador único del envío.
        id_pedido (int): Identificador del pedido asociado al envío, debe ser una clave foránea que referencia a `Pedido`.
        empresa_envio (str): Nombre de la empresa encargada del envío.
        referencia_emp_envio (str): Referencia proporcionada por la empresa de envío.
        costo_envio (decimal): Costo del envío.
        direccion (str): Dirección de envío.
        ciudad (str): Ciudad de destino del envío.
        departamento (str): Departamento de destino del envío.
        estado_envio (enum): Estado del envío, debe ser uno de los valores definidos en `EstadoEnvioEnum`.
        fecha_envio (datetime): Fecha y hora en que se registró el envío, se establece automáticamente al crear el registro.
        fecha_estimada_entrega (datetime): Fecha estimada de entrega del envío.
        fecha_entrega_real (datetime): Fecha real de entrega del envío, puede ser nula si aún no se ha entregado.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'envio'

    id_envio = db.Column('id_envio', db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column('id_pedido', db.Integer, db.ForeignKey('pedido.id_pedido'), nullable=False)
    empresa_envio = db.Column('empresa_envio', db.String(255), nullable=False)
    referencia_emp_envio = db.Column('referencia_emp_envio', db.String(255), nullable=False)
    costo_envio = db.Column('costo_envio', db.Numeric(10, 2), nullable=False)
    direccion = db.Column('direccion', db.String(255), nullable=False)
    ciudad = db.Column('ciudad', db.String(100), nullable=False)
    departamento = db.Column('departamento', db.String(100), nullable=False)
    estado_envio = db.Column('estado_envio', db.Enum('pendiente', 'en tránsito', 'entregado', 'devuelto', 'incidencia',
                                                     name='estado_envio'), nullable=False,
                             default='pendiente')
    fecha_envio = db.Column('fecha_envio', db.DateTime, server_default=db.func.now(), nullable=False)
    fecha_estimada_entrega = db.Column('fecha_estimada_entrega', db.DateTime, nullable=False)
    fecha_entrega_real = db.Column('fecha_entrega_real', db.DateTime, nullable=True)

    @validates('costo_envio')
    def validate_costo_envio(self, key, costo_envio):
        """
        Valida que el costo del envío sea un número positivo.

        Args:
            key (str): Nombre del campo.
            costo_envio (decimal): Costo del envío a validar.

        Returns:
            decimal: Costo del envío validado.

        Raises:
            ValueError: Si el costo del envío es negativo.
        """
        if costo_envio < 0:
            raise ValueError("El costo del envío debe ser un número positivo.")
        return costo_envio


class Calificacion(db.Model):
    """
    Modelo que representa una calificación de un producto por parte de un cliente.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_calificacion (int): Identificador único de la calificación.
        id_cliente (int): Identificador del cliente que realizó la calificación, debe ser una clave foránea que referencia a `Cliente`.
        id_producto (int): Identificador del producto calificado, debe ser una clave foránea que referencia a `Producto`.
        calificacion (int): Calificación otorgada al producto, debe estar entre 1 y 5.
        fecha_calificacion (datetime): Fecha y hora en que se registró la calificación, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'calificacion'

    id_calificacion = db.Column('id_calificacion', db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column('id_cliente', db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    calificacion = db.Column('calificacion', db.Integer, nullable=False)
    fecha_calificacion = db.Column('fecha_calificacion', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('calificacion')
    def validate_calificacion(self, key, calificacion):
        """
        Valida que la calificación esté entre 1 y 5.

        Args:
            key (str): Nombre del campo.
            calificacion (int): Calificación a validar.

        Returns:
            int: Calificación validada.

        Raises:
            ValueError: Si la calificación no está entre 1 y 5.
        """
        if not (1 <= calificacion <= 5):
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return calificacion


class Inventario(db.Model):
    """
    Modelo que representa el inventario de productos.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id_inventario (int): Identificador único del inventario.
        id_producto (int): Identificador del producto, debe ser una clave foránea que referencia a `Producto`.
        cantidad_total (int): Cantidad total del producto en inventario.
        cantidad_disponible (int): Cantidad disponible del producto para la venta.
        fecha_registro (datetime): Fecha y hora de registro del inventario, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'inventario'

    id_inventario = db.Column('id_inventario', db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), nullable=False,
                            unique=True)
    cantidad_total = db.Column('cantidad_total', db.Integer, nullable=False)
    cantidad_disponible = db.Column('cantidad_disponible', db.Integer, nullable=False)
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('cantidad_total', 'cantidad_disponible')
    def validate_cantidad(self, key, cantidad):
        """
        Valida que las cantidades sean números no negativos.

        Args:
            key (str): Nombre del campo.
            cantidad (int): Cantidad a validar.

        Returns:
            int: Cantidad validada.

        Raises:
            ValueError: Si la cantidad es negativa.
        """
        if cantidad < 0:
            raise ValueError(f"La {key} debe ser un número no negativo.")
        return cantidad


class AuditoriaInventario(db.Model):
    """
    Modelo que representa la auditoría del inventario de productos.

    Atributos:
        __bind_key__ (str): Enlace a la base de datos 'amaluz'.
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id (int): Identificador único de la auditoría.
        id_producto (int): Identificador del producto auditado, debe ser una clave foránea que referencia a `Producto`.
        cantidad_anterior (int): Cantidad anterior del producto antes de la modificación.
        cantidad_nueva (int): Cantidad nueva del producto después de la modificación.
        fecha_registro (datetime): Fecha y hora en que se registró la auditoría, se establece automáticamente al crear el registro.
    """
    __bind_key__ = 'amaluz'
    __tablename__ = 'auditoria_inventario'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad_anterior = db.Column('cantidad_anterior', db.Integer, nullable=False)
    cantidad_nueva = db.Column('cantidad_nueva', db.Integer, nullable=False)
    fecha_registro = db.Column('fecha_registro', db.DateTime, server_default=db.func.now(), nullable=False)

    @validates('cantidad_anterior', 'cantidad_nueva')
    def validate_cantidad(self, key, cantidad):
        """
        Valida que las cantidades sean números no negativos.

        Args:
            key (str): Nombre del campo.
            cantidad (int): Cantidad a validar.

        Returns:
            int: Cantidad validada.

        Raises:
            ValueError: Si la cantidad es negativa.
        """
        if cantidad < 0:
            raise ValueError(f"La {key} debe ser un número no negativo.")
        return cantidad
