# Este archivo contiene las rutas para los endpoints relacionados con la base de datos Amaluz
from flask import Blueprint
from app.routes.base_routes import BaseRoutes
from app.services.base_service import BaseService
from app.repositories.base_repository import BaseRepository
from app.models import (
    db, Empleado, Proveedor, Producto, Cliente, Pedido,
    DetallePedido, Envio, Calificacion, Inventario,
    AuditoriaInventario
)

# Este archivo contiene las rutas para los endpoints relacionados con la base de datos amaluz
bp = Blueprint('amaluz', __name__)

# Se crean los servicios para cada tabla
empleado_service = BaseService(BaseRepository(db, Empleado))
proveedor_service = BaseService(BaseRepository(db, Proveedor))
producto_service = BaseService(BaseRepository(db, Producto))
cliente_service = BaseService(BaseRepository(db, Cliente))
pedido_service = BaseService(BaseRepository(db, Pedido))
detallePedido_service = BaseService(BaseRepository(db, DetallePedido))
envio_service = BaseService(BaseRepository(db, Envio))
calificacion_service = BaseService(BaseRepository(db, Calificacion))
inventario_service = BaseService(BaseRepository(db, Inventario))
auditoriaInventario_service = BaseService(BaseRepository(db, AuditoriaInventario))

# Los servicios se utilizan para crear las rutas de cada tabla
empleado_routes = BaseRoutes(
    empleado_service,
    Empleado,
    ['nombre', 'correo', 'contraseña', 'telefono', 'fecha_nacimiento', 'genero', 'tipo_usuario', 'estado',
     'fecha_registro'],
    'Empleado'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de empleados
@bp.route('/empleados', methods=['GET'])
def get_empleados():
    """
    Obtiene todos los empleados.

    Returns:
        Response: Respuesta con la lista de todos los empleados.
    """
    return empleado_routes.get_all()


@bp.route('/empleados', methods=['POST'])
def add_empleado():
    """
    Agrega un nuevo empleado.

    Returns:
        Response: Respuesta con el empleado agregado.
    """
    return empleado_routes.create()


@bp.route('/empleados/<int:id>', methods=['PUT'])
def update_empleado(id):
    """
    Actualiza un empleado por ID.

    Args:
        id (int): ID del empleado a actualizar.

    Returns:
        Response: Respuesta con el empleado actualizado.
    """
    return empleado_routes.update(id)


@bp.route('/empleados/<int:id>', methods=['DELETE'])
def delete_empleado(id):
    """
    Elimina un empleado por ID.

    Args:
        id (int): ID del empleado a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return empleado_routes.delete(id)


proveedor_routes = BaseRoutes(
    proveedor_service,
    Proveedor,
    ['nombre', 'descripcion', 'telefono', 'direccion', 'fecha_registro'],
    'Proveedor'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de proveedores
@bp.route('/proveedores', methods=['GET'])
def get_proveedores():
    """
    Obtiene todos los proveedores.

    Returns:
        Response: Respuesta con la lista de todos los proveedores.
    """
    return proveedor_routes.get_all()


@bp.route('/proveedores', methods=['POST'])
def add_proveedor():
    """
    Agrega un nuevo proveedor.

    Returns:
        Response: Respuesta con el proveedor agregado.
    """
    return proveedor_routes.create()


@bp.route('/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    """
    Actualiza un proveedor por ID.

    Args:
        id (int): ID del proveedor a actualizar.

    Returns:
        Response: Respuesta con el proveedor actualizado.
    """
    return proveedor_routes.update(id)


@bp.route('/proveedores/<int:id>', methods=['DELETE'])
def delete_proveedor(id):
    """
    Elimina un proveedor por ID.

    Args:
        id (int): ID del proveedor a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return proveedor_routes.delete(id)


producto_routes = BaseRoutes(
    producto_service,
    Producto,
    ['nombre', 'precio_venta', 'categoria', 'fragancia', 'periodo_garantia', 'id_proveedor', 'fecha_registro'],
    'Producto'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de productos
@bp.route('/productos', methods=['GET'])
def get_productos():
    """
    Obtiene todos los productos.

    Returns:
        Response: Respuesta con la lista de todos los productos.
    """
    return producto_routes.get_all()


@bp.route('/productos', methods=['POST'])
def add_producto():
    """
    Agrega un nuevo producto.

    Returns:
        Response: Respuesta con el producto agregado.
    """
    return producto_routes.create()


@bp.route('/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    """
    Actualiza un producto por ID.

    Args:
        id (int): ID del producto a actualizar.

    Returns:
        Response: Respuesta con el producto actualizado.
    """
    return producto_routes.update(id)


@bp.route('/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    """
    Elimina un producto por ID.

    Args:
        id (int): ID del producto a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return producto_routes.delete(id)


cliente_routes = BaseRoutes(
    cliente_service,
    Cliente,
    ['nombre', 'telefono', 'correo', 'genero', 'fecha_nacimiento', 'fecha_registro'],
    'Cliente'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de clientes
@bp.route('/clientes', methods=['GET'])
def get_clientes():
    """
    Obtiene todos los clientes.

    Returns:
        Response: Respuesta con la lista de todos los clientes.
    """
    return cliente_routes.get_all()


@bp.route('/clientes', methods=['POST'])
def add_cliente():
    """
    Agrega un nuevo cliente.

    Returns:
        Response: Respuesta con el cliente agregado.
    """
    return cliente_routes.create()


@bp.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    """
    Actualiza un cliente por ID.

    Args:
        id (int): ID del cliente a actualizar.

    Returns:
        Response: Respuesta con el cliente actualizado.
    """
    return cliente_routes.update(id)


@bp.route('/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    """
    Elimina un cliente por ID.

    Args:
        id (int): ID del cliente a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return cliente_routes.delete(id)


pedido_routes = BaseRoutes(
    pedido_service,
    Pedido,
    ['id_cliente', 'metodo_pago', 'costo_total', 'estado', 'fecha_pedido'],
    'Pedido'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de pedidos
@bp.route('/pedidos', methods=['GET'])
def get_pedidos():
    """
    Obtiene todos los pedidos.

    Returns:
        Response: Respuesta con la lista de todos los pedidos.
    """
    return pedido_routes.get_all()


@bp.route('/pedidos', methods=['POST'])
def add_pedido():
    """
    Agrega un nuevo pedido.

    Returns:
        Response: Respuesta con el pedido agregado.
    """
    return pedido_routes.create()


@bp.route('/pedidos/<int:id>', methods=['PUT'])
def update_pedido(id):
    """
    Actualiza un pedido por ID.

    Args:
        id (int): ID del pedido a actualizar.

    Returns:
        Response: Respuesta con el pedido actualizado.
    """
    return pedido_routes.update(id)


@bp.route('/pedidos/<int:id>', methods=['DELETE'])
def delete_pedido(id):
    """
    Elimina un pedido por ID.

    Args:
        id (int): ID del pedido a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return pedido_routes.delete(id)


detallePedido_routes = BaseRoutes(
    detallePedido_service,
    DetallePedido,
    ['id_pedido', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_venta'],
    'DetallePedido'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de detalles de pedidos
@bp.route('/detalle-pedidos', methods=['GET'])
def get_detalle_pedidos():
    """
    Obtiene todos los detalles de pedidos.

    Returns:
        Response: Respuesta con la lista de todos los detalles de pedidos.
    """
    return detallePedido_routes.get_all()


@bp.route('/detalle-pedidos', methods=['POST'])
def add_detalle_pedido():
    """
    Agrega un nuevo detalle de pedido.

    Returns:
        Response: Respuesta con el detalle de pedido agregado.
    """
    return detallePedido_routes.create()


@bp.route('/detalle-pedidos/<int:id>', methods=['PUT'])
def update_detalle_pedido(id):
    """
    Actualiza un detalle de pedido por ID.

    Args:
        id (int): ID del detalle de pedido a actualizar.

    Returns:
        Response: Respuesta con el detalle de pedido actualizado.
    """
    return detallePedido_routes.update(id)


@bp.route('/detalle-pedidos/<int:id>', methods=['DELETE'])
def delete_detalle_pedido(id):
    """
    Elimina un detalle de pedido por ID.

    Args:
        id (int): ID del detalle de pedido a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return detallePedido_routes.delete(id)


envio_routes = BaseRoutes(
    envio_service,
    Envio,
    ['id_pedido', 'empresa_envio', 'referencia_emp_envio', 'costo_envio', 'direccion', 'ciudad', 'departamento',
     'estado_envio', 'fecha_estimada_entrega', 'fecha_entrega_real'],
    'Envio'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de envíos
@bp.route('/envios', methods=['GET'])
def get_envios():
    """
    Obtiene todos los envíos.

    Returns:
        Response: Respuesta con la lista de todos los envíos.
    """
    return envio_routes.get_all()


@bp.route('/envios', methods=['POST'])
def add_envio():
    """
    Agrega un nuevo envío.

    Returns:
        Response: Respuesta con el envío agregado.
    """
    return envio_routes.create()


@bp.route('/envios/<int:id>', methods=['PUT'])
def update_envio(id):
    """
    Actualiza un envío por ID.

    Args:
        id (int): ID del envío a actualizar.

    Returns:
        Response: Respuesta con el envío actualizado.
    """
    return envio_routes.update(id)


@bp.route('/envios/<int:id>', methods=['DELETE'])
def delete_envio(id):
    """
    Elimina un envío por ID.

    Args:
        id (int): ID del envío a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return envio_routes.delete(id)


calificacion_routes = BaseRoutes(
    calificacion_service,
    Calificacion,
    ['id_cliente', 'id_producto', 'calificacion', 'fecha_calificacion'],
    'Calificacion'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de calificaciones
@bp.route('/calificaciones', methods=['GET'])
def get_calificaciones():
    """
    Obtiene todas las calificaciones.

    Returns:
        Response: Respuesta con la lista de todas las calificaciones.
    """
    return calificacion_routes.get_all()


@bp.route('/calificaciones', methods=['POST'])
def add_calificacion():
    """
    Agrega una nueva calificación.

    Returns:
        Response: Respuesta con la calificación agregada.
    """
    return calificacion_routes.create()


@bp.route('/calificaciones/<int:id>', methods=['PUT'])
def update_calificacion(id):
    """
    Actualiza una calificación por ID.

    Args:
        id (int): ID de la calificación a actualizar.

    Returns:
        Response: Respuesta con la calificación actualizada.
    """
    return calificacion_routes.update(id)


@bp.route('/calificaciones/<int:id>', methods=['DELETE'])
def delete_calificacion(id):
    """
    Elimina una calificación por ID.

    Args:
        id (int): ID de la calificación a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return calificacion_routes.delete(id)


inventario_routes = BaseRoutes(
    inventario_service,
    Inventario,
    ['id_producto', 'cantidad_total', 'cantidad_disponible', 'fecha_registro'],
    'Inventario'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de inventario
@bp.route('/inventario', methods=['GET'])
def get_inventario():
    """
    Obtiene todos los registros de inventario.

    Returns:
        Response: Respuesta con la lista de todos los registros de inventario.
    """
    return inventario_routes.get_all()


@bp.route('/inventario', methods=['POST'])
def add_inventario():
    """
    Agrega un nuevo registro de inventario.

    Returns:
        Response: Respuesta con el registro de inventario agregado.
    """
    return inventario_routes.create()


@bp.route('/inventario/<int:id>', methods=['PUT'])
def update_inventario(id):
    """
    Actualiza un registro de inventario por ID.

    Args:
        id (int): ID del registro de inventario a actualizar.

    Returns:
        Response: Respuesta con el registro de inventario actualizado.
    """
    return inventario_routes.update(id)


@bp.route('/inventario/<int:id>', methods=['DELETE'])
def delete_inventario(id):
    """
    Elimina un registro de inventario por ID.

    Args:
        id (int): ID del registro de inventario a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return inventario_routes.delete(id)


auditoriaInventario_routes = BaseRoutes(
    auditoriaInventario_service,
    AuditoriaInventario,
    ['id_producto', 'cantidad_anterior', 'cantidad_nueva', 'fecha_registro'],
    'AuditoriaInventario'
)


# Se definen las rutas del método GET, POST, PUT y DELETE para la tabla de auditoría de inventario
@bp.route('/auditoria-inventario', methods=['GET'])
def get_auditoria_inventario():
    """
    Obtiene todos los registros de auditoría de inventario.

    Returns:
        Response: Respuesta con la lista de todos los registros de auditoría de inventario.
    """
    return auditoriaInventario_routes.get_all()


@bp.route('/auditoria-inventario', methods=['POST'])
def add_auditoria_inventario():
    """
    Agrega un nuevo registro de auditoría de inventario.

    Returns:
        Response: Respuesta con el registro de auditoría de inventario agregado.
    """
    return auditoriaInventario_routes.create()


@bp.route('/auditoria-inventario/<int:id>', methods=['PUT'])
def update_auditoria_inventario(id):
    """
    Actualiza un registro de auditoría de inventario por ID.

    Args:
        id (int): ID del registro de auditoría de inventario a actualizar.

    Returns:
        Response: Respuesta con el registro de auditoría de inventario actualizado.
    """
    return auditoriaInventario_routes.update(id)


@bp.route('/auditoria-inventario/<int:id>', methods=['DELETE'])
def delete_auditoria_inventario(id):
    """
    Elimina un registro de auditoría de inventario por ID.

    Args:
        id (int): ID del registro de auditoría de inventario a eliminar.

    Returns:
        Response: Respuesta con el estado de la eliminación.
    """
    return auditoriaInventario_routes.delete(id)
