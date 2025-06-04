USE amaluz;

#PREGUNTA DE NEGOCIOS Y CONSULTA

#Tabla Empleados
#Pregunta de Negocio
#¿Cuántos empleados hay teniendo en cuenta el tipo de usuario?
SELECT tipo_usuario, COUNT(*) AS cantidad_empleados
FROM EMPLEADO
WHERE estado = 'activo'
GROUP BY tipo_usuario
ORDER BY cantidad_empleados DESC;


#Pregunta de Consulta
#¿Cuantos empleados están trabajando actualmente?
SELECT COUNT(*) AS empleados_activos
FROM EMPLEADO
WHERE estado = 'activo';


#TABLA PROVEEDORES
#Pregunta Negocio
#¿Qué proveedores podrían estar afectando mis costos de producción?


#¿De qué proveedor dependo más?


#Pregunta Consulta
#¿Cuál es la distribución de proveedores por ciudad o zona?
SELECT direccion, COUNT(*) AS cantidad
FROM PROVEEDOR
GROUP BY direccion
ORDER BY cantidad DESC;

#¿Cuántos proveedores están registrados actualmente? 

SELECT COUNT(*) AS total_proveedores
FROM PROVEEDOR;

#TABLA PRODUCTOS
#Preguntas de Negocio
#¿Existen categorías de productos que no tienen rotación y podríamos dejar de ofrecer?
SELECT p.categoria
FROM PRODUCTOS p
LEFT JOIN DETALLE_PEDIDO dp ON p.id_producto = dp.id_producto
WHERE dp.id_producto IS NULL
GROUP BY p.categoria;

#¿Qué fragancias son las más populares o más frecuentes en el catálogo?
SELECT fragancia, COUNT(*) AS cantidad_productos
FROM PRODUCTOS
GROUP BY fragancia
ORDER BY cantidad_productos DESC;


#Preguntas Consultas
#¿Cuál es el producto más barato y el más caro?
SELECT nombre, precio_venta
FROM PRODUCTOS
ORDER BY precio_venta ASC
LIMIT 1;
SELECT nombre, precio_venta
FROM PRODUCTOS
ORDER BY precio_venta DESC
LIMIT 1;

#¿Cuáles son los 10 producto más comprados por los clientes?
SELECT 
    p.nombre AS producto,
    SUM(dp.cantidad) AS total_comprado
FROM DETALLE_PEDIDO dp
JOIN PRODUCTOS p ON dp.id_producto = p.id_producto
GROUP BY p.nombre
ORDER BY total_comprado DESC
LIMIT 10;


#Tabla Clientes
#PREGUNTAS DE NEGOCIO
#¿Qué clientes cumplen años en el mes actual? Para promociones especiales.
SELECT nombre, correo, telefono, fecha_nacimiento
FROM CLIENTE
WHERE MONTH(fecha_nacimiento) = MONTH(CURDATE());

#¿Cuál es el rango de edad más común entre los clientes?
SELECT 
  CASE 
    WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
    WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 26 AND 35 THEN '26-35'
    WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 36 AND 45 THEN '36-45'
    WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 46 AND 60 THEN '46-60'
    ELSE '60+'
  END AS grupo_edad,
  COUNT(*) AS cantidad_clientes
FROM CLIENTE
GROUP BY grupo_edad
ORDER BY cantidad_clientes DESC;

#PREGUNTAS DE CONSULTA
#¿Clientes duplicados (mismo correo o teléfono)? (Para limpieza de base)
SELECT correo, telefono, COUNT(*) AS cantidad
FROM CLIENTE
WHERE correo IS NOT NULL OR telefono IS NOT NULL
GROUP BY correo, telefono
HAVING cantidad > 1;

#¿Cuántos clientes se han registrado en total?
SELECT COUNT(*) AS total_clientes
FROM CLIENTE;

#TABLA PEDIDO
#PREGUNTAS DE NEGOCIO
#¿Cuántos pedidos han sido cancelados o reembolsados?

SELECT COUNT(*) AS total_perdidos
FROM PEDIDO
WHERE estado IN ('cancelado', 'reembolsado');

#¿Qué clientes han tenido mayor actividad de pedidos en los últimos 6 meses, y podrían ser buenos candidatos para una campaña de fidelización o recompensas?
SELECT 
    c.id_cliente,
    c.nombre,
    c.correo,
    COUNT(p.id_pedido) AS total_pedidos
FROM 
    CLIENTE c
JOIN 
    PEDIDO p ON c.id_cliente = p.id_cliente
WHERE 
    p.fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY 
    c.id_cliente, c.nombre, c.correo
ORDER BY 
    total_pedidos DESC;


#PREGUNTAS DE CONSULTA
#¿Cuántos pedidos se han hecho por mes?
SELECT DATE_FORMAT(fecha_pedido, '%Y-%m') AS mes, COUNT(*) AS total_pedidos
FROM PEDIDO
GROUP BY mes
ORDER BY mes;

#¿Cuántos clientes han realizado pedidos más de una vez?
SELECT COUNT(DISTINCT id_cliente) AS clientes_frecuentes
FROM PEDIDO
WHERE id_cliente IN (
    SELECT id_cliente
    FROM PEDIDO
    GROUP BY id_cliente
    HAVING COUNT(*) > 1
);

#TABLA DETALLE PEDIDO
#PREGUNTA NEGOCIO
#¿En qué rangos de precio están los productos que más se venden y podemos usarlos como referencia para nuevos lanzamientos? 
SELECT 
    CASE 
        WHEN precio_unitario < 10000 THEN 'Menos de $10.000'
        WHEN precio_unitario BETWEEN 10000 AND 19999 THEN '$10.000 - $19.999'
        WHEN precio_unitario BETWEEN 20000 AND 29999 THEN '$20.000 - $29.999'
        WHEN precio_unitario BETWEEN 30000 AND 39999 THEN '$30.000 - $39.999'
        ELSE 'Más de $40.000'
    END AS rango_precio,
    SUM(cantidad) AS total_unidades_vendidas,
    SUM(subtotal) AS total_ingresos
FROM DETALLE_PEDIDO
GROUP BY rango_precio
ORDER BY total_unidades_vendidas DESC;

#¿Qué productos están generando más ingresos por unidad vendida, y deberíamos potenciarlos en futuras campañas?
SELECT 
    p.id_producto,
    p.nombre AS nombre_producto,
    ROUND(SUM(dp.subtotal) / SUM(dp.cantidad), 2) AS ingreso_por_unidad,
    SUM(dp.cantidad) AS unidades_totales_vendidas,
    SUM(dp.subtotal) AS ingreso_total
FROM DETALLE_PEDIDO dp
JOIN PRODUCTOS p ON dp.id_producto = p.id_producto
GROUP BY p.id_producto, p.nombre
HAVING unidades_totales_vendidas > 0
ORDER BY ingreso_por_unidad DESC
LIMIT 10;


#PREGUNTAS DE CONSULTAS
#¿Cuál es el total de ingresos generados por la empresa?
SELECT SUM(subtotal) AS ingresos_totales
FROM DETALLE_PEDIDO;

#¿Cuál ha sido el mes con mayores pedidos?
SELECT 
    DATE_FORMAT(fecha_venta, '%Y-%m') AS mes,
    SUM(subtotal) AS total_ventas
FROM DETALLE_PEDIDO
GROUP BY mes
ORDER BY total_ventas DESC
LIMIT 1;

#TABLA ENVIOS
#PREGUNTA DE NEGOCIO
#¿Qué empresas de envío están funcionando mejor y cuáles deberíamos evitar para no afectar la experiencia del cliente?
SELECT empresa_envio,
       COUNT(*) AS total_entregas,
       SUM(CASE WHEN fecha_entrega_real <= fecha_estimada_entrega THEN 1 ELSE 0 END) AS puntuales,
       SUM(CASE WHEN fecha_entrega_real > fecha_estimada_entrega THEN 1 ELSE 0 END) AS tardias,
       ROUND(SUM(CASE WHEN fecha_entrega_real <= fecha_estimada_entrega THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS porcentaje_puntualidad
FROM ENVIO
WHERE estado_envio = 'entregado'
GROUP BY empresa_envio
ORDER BY porcentaje_puntualidad DESC;

#

#PREGUNTA CONSULTA
#¿Cuántos pedidos se han enviado con envío gratis vs envío estándar?
SELECT costo_envio, COUNT(*) AS cantidad_envios
FROM ENVIO
GROUP BY costo_envio;

#¿A qué ciudades o departamentos se realizan más envíos?
SELECT ciudad AS lugar, COUNT(*) AS total_envios, 'Ciudad' AS tipo
FROM ENVIO
GROUP BY ciudad
UNION ALL
SELECT departamento AS lugar, COUNT(*) AS total_envios, 'Departamento' AS tipo
FROM ENVIO
GROUP BY departamento
ORDER BY total_envios DESC;



#TABLA COMENTARIOS Y CALIFICACIONES



#TABLA HISTORIAL METODOS ENVIOS