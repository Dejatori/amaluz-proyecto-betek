# Diseño de una Base de Datos para la Gestión de un Comercio Online de Venta de Velas

## Enunciado del Proyecto

Se requiere el diseño de una base de datos integral para un comercio online dedicado a la venta de velas artesanales y
decorativas, con cobertura de envíos a nivel nacional en Colombia. El objetivo principal es centralizar y gestionar de
manera eficiente toda la información relacionada con los productos, clientes, pedidos, inventario, proveedores y envíos,
garantizando una experiencia de compra fluida y un servicio al cliente de alta calidad.

La base de datos debe permitir almacenar y administrar información detallada sobre los productos, incluyendo nombre,
precio, categoría, fragancia, periodo de garantía y proveedor asociado. También es necesario registrar y gestionar los
datos de los clientes, como nombre, correo, teléfono, fecha de nacimiento e historial de compras, para ofrecer un
servicio más personalizado.

El sistema debe facilitar la gestión de los pedidos realizados a través de la plataforma online, registrando detalles
como fecha, productos seleccionados, cantidad, costo total, método de pago y estado del pedido (pendiente, procesando,
enviado, entregado, cancelado o reembolsado). Además, se debe integrar un módulo de seguimiento de envíos que permita
registrar la empresa transportadora, número de guía, dirección de entrega, ciudad, estado del envío y fechas estimadas y
reales de entrega.

Se requiere un módulo de inventario que permita llevar un control preciso de las existencias de cada producto, registrar
movimientos y auditorías, y generar alertas ante niveles bajos de stock. También es importante contar con la posibilidad
de que los clientes califiquen los productos adquiridos, para medir la satisfacción y mejorar la oferta.

Finalmente, la base de datos debe ser compatible con herramientas de análisis y visualización como Power BI, permitiendo
generar reportes sobre ventas, productos más vendidos, clientes frecuentes, niveles de inventario y tiempos de entrega.
El diseño debe garantizar la seguridad, integridad y confidencialidad de la información, así como la escalabilidad para
adaptarse a futuras necesidades del negocio, como la incorporación de nuevos productos o canales de venta.

## Descripción del proyecto

El proyecto consiste en el diseño e implementación de una base de datos relacional para el comercio online **Amaluz.**
El sistema integrará tecnologías como Python con Flask (backend), Tkinter (Interfaz gráfica), MySQL/Azure SQL
Databases (base de datos) y Power BI (visualización) para optimizar la gestión de productos, clientes, pedidos,
inventario y logística.
El objetivo es ofrecer una solución escalable que garantice una experiencia de análisis de datos accionables y soporte
para decisiones estratégicas.

## Objetivo general del proyecto

Desarrollar un sistema integral que permita gestionar eficientemente la operación de un comercio online de velas,
integrando una base de datos robusta, una interfaz interactiva para sus empleados y un dashboard analítico para
monitorear métricas clave del negocio.

## Objetivos específicos del proyecto

1. Diseñar un diagrama Entidad-Relación (ER) y un modelo relacional para representar las entidades y relaciones
   fundamentales del negocio (productos, clientes, pedidos, inventario, etc.).
2. Implementar la base de datos en MySQL a través de scripts DDL (creación de tablas) y DML (inserción de datos de
   prueba).
3. Analizar preguntas de negocio utilizando consultas SQL avanzadas (agregaciones, joins, subconsultas) para obtener
   insights accionables.
4. Crear un dashboard interactivo en Power BI que muestre métricas clave como ventas mensuales, productos más vendidos,
   niveles de stock crítico y tiempos de entrega.
5. Asegurar la seguridad, escalabilidad y eficiencia del sistema para adaptarse a futuras expansiones (por ejemplo:
   nuevos productos o canales de venta).

## Alcance del proyecto

El proyecto abarcará el diseño, implementación y documentación de una base de datos relacional para el comercio online *
*Amaluz**, cubriendo los siguientes aspectos:

- **Modelado de datos:** Elaboración del diagrama Entidad-Relación (ER) y el modelo relacional que representen de forma
  precisa las entidades, atributos y relaciones fundamentales del negocio, tales como productos, clientes, empleados,
  proveedores, pedidos, envíos, inventario y auditoría de inventario.
- **Implementación en base de datos:** Creación de la base de datos en MySQL mediante scripts DDL para la definición de
  tablas, restricciones y relaciones, así como scripts DML para la inserción de datos de prueba representativos.
- **Desarrollo de consultas y análisis:** Formulación de consultas SQL avanzadas para responder preguntas de negocio
  relevantes, incluyendo análisis de ventas, gestión de inventario, seguimiento de pedidos, identificación de productos
  más vendidos y clientes frecuentes.
- **Visualización y reportes:** Integración con Power BI para la creación de dashboards interactivos que permitan
  visualizar métricas clave del negocio, como ventas por período, niveles de stock, tiempos de entrega y satisfacción
  del cliente.
- **Seguridad y confidencialidad:** Implementación de buenas prácticas para garantizar la integridad, seguridad y
  confidencialidad de la información almacenada, incluyendo el control de acceso y la protección de datos sensibles.
- **Documentación técnica:** Elaboración de documentación clara y estructurada que describa el proceso de diseño, la
  estructura de la base de datos, las reglas de negocio, ejemplos de consultas y el uso de las herramientas de análisis.
- **Escalabilidad y mantenimiento:** Diseño de la solución considerando la posibilidad de futuras expansiones, como la
  incorporación de nuevos productos, funcionalidades, usuarios o canales de venta, asegurando la flexibilidad y
  adaptabilidad del sistema.

Quedan fuera del alcance el desarrollo de la plataforma web de ventas, la integración con pasarelas de pago reales y la
automatización de procesos logísticos externos, aunque se dejarán sentadas las bases para su posible implementación
futura.

## Misión

Brindar a nuestros clientes una experiencia de compra única mediante una amplia selección de velas artesanales y
decorativas de la más alta calidad. Nos enfocamos en ofrecer un servicio al cliente personalizado y una logística
eficiente que garantice entregas rápidas y seguras en todo el territorio colombiano. Nos comprometemos a innovar
continuamente en nuestros productos y procesos para anticipar y satisfacer las necesidades de nuestros consumidores,
promoviendo la sostenibilidad y apoyando activamente a los artesanos locales.

## Visión

Convertirnos en el comercio online líder en la venta de velas artesanales y decorativas en Colombia, reconocido por
nuestra innovación, calidad de productos y excelencia en el servicio al cliente, así como por nuestra capacidad de
adaptarnos a las tendencias del mercado y las necesidades de nuestros consumidores expandiendo nuestra presencia a nivel
nacional e internacional.

## Objetivos estratégicos

1. **Crecimiento y posicionamiento digital:** Consolidar a Amaluz como referente nacional en la venta online de velas
   artesanales y decorativas, incrementando la presencia digital y alcanzando un crecimiento sostenido del 20% anual en
   ventas.
2. **Innovación basada en datos:** Desarrollar nuevas líneas de productos y servicios apoyados en el análisis de datos
   de clientes y tendencias de mercado, lanzando al menos 5 innovaciones anuales.
3. **Excelencia en la experiencia del cliente:** Mejorar la personalización y satisfacción del cliente mediante el uso
   de información centralizada, logrando una tasa de satisfacción superior al 90% y optimizando el proceso de compra y
   atención.
4. **Optimización logística y operativa:** Reducir el tiempo promedio de entrega a menos de 3 días hábiles y minimizar
   incidencias, utilizando la base de datos para monitorear y mejorar continuamente la cadena logística.
5. **Sostenibilidad y apoyo a la comunidad:** Implementar prácticas sostenibles en la producción y distribución,
   reduciendo la huella de carbono en un 15% en 5 años y fortaleciendo la colaboración con artesanos locales mediante
   programas de capacitación y seguimiento.

## Justificación del proyecto

La implementación de una base de datos integral es fundamental para que Amaluz consolide su posición en el mercado de
velas artesanales y decorativas en Colombia. La gestión eficiente y centralizada de la información permitirá optimizar
procesos clave como el control de inventario, la atención al cliente, la personalización de la oferta y la logística de
envíos, aspectos esenciales para garantizar una experiencia de compra superior y fortalecer la fidelización.

El uso de herramientas tecnológicas como bases de datos relacionales y dashboards analíticos en Power BI facilitará la
toma de decisiones estratégicas basadas en datos reales, permitiendo identificar tendencias de consumo, anticipar la
demanda, gestionar promociones y mejorar la eficiencia operativa. Además, la digitalización de los procesos contribuirá
a la sostenibilidad del negocio, al reducir errores, minimizar desperdicios y apoyar la trazabilidad de productos y
materias primas.

Este proyecto también responde a la necesidad de escalar el modelo de negocio de Amaluz, preparándolo para futuras
expansiones, la incorporación de nuevos canales de venta y la integración con plataformas tecnológicas modernas. Así, la
solución propuesta no solo apoya el crecimiento y la innovación, sino que refuerza el compromiso de Amaluz con la
calidad, la sostenibilidad y el desarrollo de la comunidad artesanal local.

## Equipo de trabajo

El equipo de trabajo estará conformado por los siguientes roles clave, enfocados en el diseño, implementación y análisis
de la base de datos para Amaluz:

- **Líder de Proyecto:** Supervisa la planificación, coordinación y cumplimiento de los objetivos del proyecto,
  asegurando la alineación con la visión de Amaluz.
- **Analista de Datos:** Encargado de identificar los requerimientos de información, definir indicadores clave y
  proponer consultas y reportes relevantes para la toma de decisiones.
- **Diseñador de Base de Datos:** Responsable de modelar y estructurar la base de datos, garantizando la integridad,
  eficiencia y escalabilidad del sistema.
- **Desarrollador Backend:** Implementa la lógica de negocio y las interfaces de acceso a la base de datos utilizando
  Python y Flask.
- **Desarrollador de Interfaces:** Desarrolla la interfaz gráfica para la gestión interna (Tkinter) y apoya la
  integración con herramientas de visualización.
- **Especialista en Visualización de Datos:** Diseña dashboards y reportes interactivos en Power BI para monitorear
  ventas, inventario y desempeño logístico.
- **Administrador de Base de Datos (DBA):** Gestiona la seguridad, mantenimiento y respaldo de la base de datos,
  asegurando su disponibilidad y protección.
- **Documentador Técnico:** Elabora la documentación del modelo de datos, reglas de negocio, ejemplos de consultas y
  manuales de usuario para facilitar el uso y mantenimiento del sistema.

Este equipo está orientado a cubrir todas las etapas del ciclo de vida del proyecto, desde el análisis y diseño hasta la
implementación, análisis y documentación, asegurando que la solución responda a las necesidades de gestión y crecimiento
de Amaluz.

## Esquema de la base de datos Amaluz – Entidades y Atributos

![Esquema de la base de datos Amaluz](amaluz_schema.md)

## Diagrama Entidad-Relación (ER)

![Diagrama ER de la base de datos Amaluz](https://tinyurl.com/amaluz)

## Script DDL (Data Definition Language)

![Script DDL de la base de datos Amaluz](../../db/mysql/amaluz_ddl.sql)

## Script DML (Data Manipulation Language)

![Script DML de la base de datos Amaluz](../../db/mysql/amaluz_dml.sql)

## Beneficios y Valor Agregado del Proyecto

**Eficiencia operativa:**  
La automatización de procesos clave, como la gestión de inventario, pedidos y seguimiento de envíos, optimizará el uso
de recursos y reducirá errores, permitiendo al equipo de Amaluz enfocarse en la innovación y la atención personalizada.

**Experiencia del cliente:**  
La integración de una interfaz intuitiva y un proceso de compra ágil incrementará la satisfacción y fidelización de los
clientes, facilitando la personalización de ofertas y el seguimiento de pedidos en tiempo real.

**Personalización y fidelización:**  
El análisis de datos sobre preferencias y comportamientos de compra permitirá ofrecer recomendaciones y promociones
personalizadas, fortaleciendo la relación con los clientes y aumentando la recurrencia de compra.

**Toma de decisiones basada en datos:**  
El acceso a reportes y dashboards en tiempo real facilitará la identificación de tendencias, productos más demandados y
oportunidades de mejora, apoyando la toma de decisiones estratégicas para el crecimiento de Amaluz.

**Escalabilidad y adaptabilidad:**  
La arquitectura propuesta permitirá incorporar nuevos productos, categorías y funcionalidades, así como adaptarse a la
expansión hacia nuevos mercados o canales de venta, sin afectar el rendimiento del sistema.

**Seguridad y confianza:**  
Se implementarán medidas robustas de seguridad y protección de datos, garantizando la confidencialidad de la información
de clientes, transacciones y proveedores, y fortaleciendo la reputación de Amaluz como empresa confiable y responsable.

**Impacto social y sostenibilidad:**  
La digitalización de procesos apoyará la trazabilidad de productos artesanales y la colaboración con proveedores
locales, promoviendo prácticas sostenibles y el desarrollo de la comunidad artesanal.
