-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS amaluz;

-- Usar la base de datos
USE amaluz;

-- Tabla de empleados

CREATE TABLE EMPLEADO
(
    id_empleado      INT PRIMARY KEY AUTO_INCREMENT,
    nombre           VARCHAR(255)                                      NOT NULL,
    correo           VARCHAR(255)                                      NOT NULL UNIQUE,
    contraseña       VARCHAR(255)                                      NOT NULL,
    telefono         VARCHAR(20)                                       NOT NULL,
    fecha_nacimiento DATE                                              NOT NULL,
    genero           ENUM ('masculino', 'femenino', 'otro')            NOT NULL,
    tipo_usuario     ENUM ('propietario', 'administrador', 'empleado') NOT NULL,
    estado           ENUM ('activo', 'inactivo', 'eliminado')          NOT NULL DEFAULT 'activo',
    fecha_registro   DATETIME                                          NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Proveedores
CREATE TABLE PROVEEDOR
(
    id_proveedor   INT PRIMARY KEY AUTO_INCREMENT,
    nombre         VARCHAR(255) NOT NULL,
    descripcion    TEXT         NOT NULL,
    telefono       VARCHAR(20)  NOT NULL,
    direccion      VARCHAR(255) NOT NULL,
    fecha_registro DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Productos
CREATE TABLE PRODUCTOS
(
    id_producto      INT PRIMARY KEY AUTO_INCREMENT,
    nombre           VARCHAR(255)                                               NOT NULL,
    precio_venta     DECIMAL(10, 2)                                             NOT NULL CHECK (precio_venta >= 0),
    categoria        ENUM
                         ('Velas Aromáticas', 'Velas Decorativas',
                             'Velas Artesanales', 'Velas Personalizadas',
                             'Velas de Recordatorio')                           NOT NULL,
    fragancia        ENUM
                         ('Lavanda', 'Rosa', 'Cítricos', 'Vainilla',
                             'Chocolate', 'Eucalipto', 'Menta', 'Canela',
                             'Café', 'Tropical', 'Jazmín', 'Bebé', 'Sándalo',
                             'Pino', 'Naturaleza', 'Sofe', 'Cítricos Frescos',
                             'Frutos Rojos', 'Frutos Amarillos','Romero',
                             'Especias', 'Chicle', 'Coco', 'Tabaco & Chanelle') NOT NULL,
    periodo_garantia INT                                                        NOT NULL CHECK (periodo_garantia >= 0),
    id_proveedor     INT                                                        NOT NULL,
    fecha_registro   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_proveedor) REFERENCES PROVEEDOR (id_proveedor) ON DELETE CASCADE
);

-- Tabla cliente
CREATE TABLE CLIENTE
(
    id_cliente       INT PRIMARY KEY AUTO_INCREMENT,
    nombre           VARCHAR(255)                           NOT NULL,
    telefono         VARCHAR(20)                            NOT NULL,
    correo           VARCHAR(255)                           NOT NULL UNIQUE,
    genero           ENUM ('Masculino', 'Femenino', 'Otro') NOT NULL,
    fecha_nacimiento DATE                                   NOT NULL,
    fecha_registro   DATETIME                               NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Pedidos
CREATE TABLE PEDIDO
(
    id_pedido    INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente   INT                                                                                  NOT NULL,
    metodo_pago  ENUM ('Tarjeta de Crédito', 'Transferencia Bancaria', 'PSE')                         NOT NULL,
    costo_total  DECIMAL(10, 2)                                                                       NOT NULL CHECK (costo_total >= 0),
    estado       ENUM ('pendiente', 'procesando', 'enviado', 'entregado', 'cancelado', 'reembolsado') NOT NULL DEFAULT 'pendiente',
    fecha_pedido DATETIME                                                                             NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente) ON DELETE CASCADE
);

-- Tabla de Detalle de Pedido
CREATE TABLE DETALLE_PEDIDO
(
    id_detalle      INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido       INT            NOT NULL,
    id_producto     INT            NOT NULL,
    cantidad        INT            NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal        DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    fecha_venta     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES PEDIDO (id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES PRODUCTOS (id_producto) ON DELETE CASCADE
);


-- Tabla de Envíos
CREATE TABLE ENVIO
(
    id_envio               INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido              INT                                                                      NOT NULL,
    empresa_envio          VARCHAR(255)                                                             NOT NULL,
    referencia_emp_envio   VARCHAR(255)                                                             NOT NULL,
    costo_envio            DECIMAL(10, 2)                                                           NOT NULL CHECK (costo_envio >= 0),
    direccion              VARCHAR(255)                                                             NOT NULL,
    ciudad                 VARCHAR(100)                                                             NOT NULL,
    departamento           VARCHAR(100)                                                             NOT NULL,
    estado_envio           ENUM ('pendiente', 'en tránsito', 'entregado', 'devuelto', 'incidencia') NOT NULL DEFAULT 'pendiente',
    fecha_envio            DATETIME                                                                 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada_entrega DATETIME                                                                 NOT NULL,
    fecha_entrega_real     DATETIME                                                                          DEFAULT NULL,
    FOREIGN KEY (id_pedido) REFERENCES PEDIDO (id_pedido) ON DELETE CASCADE
);

-- Tabla de calificacion
CREATE TABLE CALIFICACION
(
    id_calificacion    INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente         INT      NOT NULL,
    id_producto        INT      NOT NULL,
    calificacion       INT      NOT NULL CHECK (calificacion >= 1 AND calificacion <= 5),
    fecha_calificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES PRODUCTOS (id_producto) ON DELETE CASCADE
);

-- Tabla inventario
CREATE TABLE INVENTARIO
(
    id_inventario       INT PRIMARY KEY AUTO_INCREMENT,
    id_producto         INT      NOT NULL UNIQUE,
    cantidad_total      INT      NOT NULL CHECK (cantidad_total >= 0),
    cantidad_disponible INT      NOT NULL CHECK (cantidad_disponible >= 0),
    fecha_registro      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES PRODUCTOS (id_producto) ON DELETE CASCADE,
    CHECK (cantidad_disponible <= cantidad_total)
);


-- Tabla auditoria inventario 
CREATE TABLE AUDITORIA_INVENTARIO
(
    id                INT PRIMARY KEY AUTO_INCREMENT,
    id_producto       INT      NOT NULL,
    cantidad_anterior INT      NOT NULL CHECK (cantidad_anterior >= 0),
    cantidad_nueva    INT      NOT NULL CHECK (cantidad_nueva >= 0),
    fecha_registro    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES PRODUCTOS (id_producto) ON DELETE CASCADE
);