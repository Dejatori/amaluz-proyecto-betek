-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS dbo;

-- Usar la base de datos
USE dbo;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(150) NOT NULL,
    correo              VARCHAR(100) NOT NULL UNIQUE,
    contrasena          VARCHAR(255) NOT NULL,
    telefono            VARCHAR(15)  NOT NULL UNIQUE,
    fecha_nacimiento    DATE         NOT NULL,
    genero              ENUM
                            ('Masculino', 'Femenino', 'Otro'),
    tipo_usuario        ENUM
                            ('Cliente', 'Administrador', 'Vendedor')       DEFAULT 'Cliente',
    estado              ENUM
                            ('Activo', 'Inactivo',
                                'Bloqueado', 'Eliminado', 'Sin confirmar') DEFAULT 'Sin confirmar',
    fecha_registro      TIMESTAMP                                          DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP                                          DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Auditoría de Usuarios
CREATE TABLE IF NOT EXISTS auditoria_usuarios
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id      INT NOT NULL,
    estado_anterior ENUM ('Activo', 'Inactivo', 'Bloqueado', 'Eliminado', 'Sin confirmar') DEFAULT 'Sin confirmar',
    estado_nuevo    ENUM ('Activo', 'Inactivo', 'Bloqueado', 'Eliminado', 'Sin confirmar') DEFAULT 'Sin confirmar',
    fecha_cambio    TIMESTAMP                                             DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Proveedores
CREATE TABLE IF NOT EXISTS proveedores
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(150) NOT NULL,
    telefono            VARCHAR(15)  NOT NULL,
    direccion           VARCHAR(255) NOT NULL,
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(150)                                               NOT NULL,
    descripcion         TEXT                                                       NOT NULL,
    precio_venta        DECIMAL(10, 2) CHECK (precio_venta > 0)                    NOT NULL,
    categoria           ENUM
                            ('Velas Aromáticas', 'Velas Decorativas',
                                'Velas Artesanales', 'Velas Personalizadas',
                                'Velas de Recordatorio')                           NOT NULL,
    peso                DECIMAL(5, 2)                                              NOT NULL,
    dimensiones         VARCHAR(50)                                                NOT NULL,
    imagen_url          VARCHAR(255)                                               NOT NULL,
    fragancia           ENUM
                            ('Lavanda', 'Rosa', 'Cítricos', 'Vainilla',
                                'Chocolate', 'Eucalipto', 'Menta', 'Canela',
                                'Café', 'Tropical', 'Jazmín', 'Bebé', 'Sándalo',
                                'Pino', 'Naturaleza', 'Sofe', 'Cítricos Frescos',
                                'Frutos Rojos', 'Frutos Amarillos','Romero',
                                'Especias', 'Chicle', 'Coco', 'Tabaco & Chanelle') NOT NULL,
    periodo_garantia    INT                                                        NOT NULL DEFAULT 90,
    estado              ENUM ('Activo', 'Inactivo')                                NOT NULL DEFAULT 'Activo',
    precio_proveedor    DECIMAL(10, 2) CHECK (precio_proveedor > 0)                NOT NULL,
    proveedor_id        INT,
    fecha_registro      TIMESTAMP                                                           DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP                                                           DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CHECK (precio_venta > precio_proveedor),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabla de Auditoría de Productos
CREATE TABLE IF NOT EXISTS auditoria_productos
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    producto_id     INT            NOT NULL,
    precio_anterior DECIMAL(10, 2) NOT NULL,
    precio_nuevo    DECIMAL(10, 2) NOT NULL,
    estado_anterior ENUM ('Activo', 'Inactivo') DEFAULT 'Activo',
    estado_nuevo    ENUM ('Activo', 'Inactivo') DEFAULT 'Activo',
    fecha_cambio    TIMESTAMP                   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Inventario
CREATE TABLE IF NOT EXISTS inventario
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    producto_id         INT NOT NULL UNIQUE,
    cantidad_mano       INT NOT NULL DEFAULT 0,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    fecha_registro      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Auditoría de Inventario
CREATE TABLE IF NOT EXISTS auditoria_inventario
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    producto_id       INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva    INT NOT NULL,
    fecha_cambio      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Localización de Pedido (Direcciones)
CREATE TABLE IF NOT EXISTS localizacion_pedido
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT          NOT NULL,
    direccion_1         VARCHAR(255) NOT NULL,
    direccion_2         VARCHAR(255),
    ciudad              VARCHAR(100) NOT NULL,
    departamento        VARCHAR(100) NOT NULL,
    codigo_postal       VARCHAR(10)  NOT NULL,
    descripcion         TEXT,
    notas_entrega       TEXT,
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Pedidos
CREATE TABLE IF NOT EXISTS pedidos
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT                                                         NOT NULL,
    id_localizacion     INT                                                         NOT NULL,
    codigo_pedido       VARCHAR(50)                                                 NOT NULL UNIQUE,
    costo_total         DECIMAL(10, 2)                                              NOT NULL,
    metodo_pago         ENUM
                            ('Tarjeta de Crédito', 'Transferencia Bancaria', 'PSE') NOT NULL,
    estado_pedido       ENUM
                            ('Pendiente', 'Procesando', 'Enviado',
                                'Entregado', 'Cancelado', 'Reembolsado') DEFAULT 'Pendiente',
    fecha_registro      TIMESTAMP                                        DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP                                        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_localizacion) REFERENCES localizacion_pedido (id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabla de Detalle de Pedido
CREATE TABLE IF NOT EXISTS detalle_pedido
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id           INT            NOT NULL,
    producto_id         INT            NOT NULL,
    cantidad            INT            NOT NULL CHECK (cantidad > 0),
    precio_unitario     DECIMAL(10, 2) NOT NULL,
    subtotal            DECIMAL(10, 2) NOT NULL,
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE (pedido_id, producto_id)
);

-- Tabla de Auditoría de Pedidos
CREATE TABLE IF NOT EXISTS auditoria_pedidos
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id       INT                                                                                  NOT NULL,
    estado_anterior ENUM ('Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado', 'Reembolsado') NOT NULL,
    estado_nuevo    ENUM ('Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado', 'Reembolsado') NOT NULL,
    fecha_cambio    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Descuentos
CREATE TABLE IF NOT EXISTS descuentos
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    codigo_descuento    VARCHAR(50)   NOT NULL UNIQUE,
    porcentaje          DECIMAL(5, 2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    fecha_inicio        TIMESTAMP     NOT NULL,
    fecha_fin           TIMESTAMP     NOT NULL,
    estado              ENUM ('Activo', 'Inactivo') DEFAULT 'Activo',
    fecha_registro      TIMESTAMP                   DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP                   DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (fecha_fin >= fecha_inicio)
);

-- Tabla de Historial de Descuentos
CREATE TABLE IF NOT EXISTS historial_descuentos
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT NOT NULL,
    descuento_id        INT NOT NULL,
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (descuento_id) REFERENCES descuentos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Carrito de Compras
CREATE TABLE IF NOT EXISTS carrito
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT NOT NULL,
    producto_id         INT NOT NULL,
    cantidad            INT NOT NULL CHECK (cantidad > 0),
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (usuario_id, producto_id)
);

-- Tabla de Comentarios y Calificaciones
CREATE TABLE IF NOT EXISTS comentarios
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT  NOT NULL,
    producto_id         INT  NOT NULL,
    comentario          TEXT NOT NULL,
    calificacion        INT CHECK (calificacion >= 1 AND calificacion <= 5),
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Envíos
CREATE TABLE IF NOT EXISTS envios
(
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id              INT            NOT NULL UNIQUE,
    empresa_envio          VARCHAR(100)   NOT NULL,
    numero_guia            VARCHAR(50)    NOT NULL UNIQUE,
    costo_envio            DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    fecha_envio            TIMESTAMP      NULL,
    fecha_entrega_estimada TIMESTAMP      NULL,
    fecha_entrega_real     TIMESTAMP      NULL,
    estado_envio           ENUM ('Pendiente',
        'En tránsito', 'Entregado', 'Devuelto',
        'Incidencia')                              DEFAULT 'Pendiente',
    fecha_registro         TIMESTAMP               DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion    TIMESTAMP               DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Historial de Métodos de Envío
CREATE TABLE IF NOT EXISTS historial_metodos_envio
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT            NOT NULL,
    empresa_envio       VARCHAR(100)   NOT NULL,
    costo_envio         DECIMAL(10, 2) NOT NULL CHECK (costo_envio >= 0),
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
);
