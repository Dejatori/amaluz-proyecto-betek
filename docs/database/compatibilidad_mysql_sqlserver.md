# Compatibilidad entre MySQL y SQL Server en el proyecto

## Problemas identificados

Durante la implementación del proyecto "Gestión de Comercio Online de Velas" se identificaron varios problemas de
compatibilidad entre MySQL y SQL Server:

1. **Error de sintaxis con la cláusula `RESTRICT`**: SQL Server no soporta la cláusula `ON DELETE RESTRICT` que sí es
   soportada por MySQL. En SQL Server, se debe usar `ON DELETE NO ACTION` que tiene un comportamiento similar.

2. **Error con restricciones de clave foránea que causan ciclos o múltiples rutas en cascada**: SQL Server no permite
   ciclos o múltiples rutas en cascada en las relaciones de clave foránea. Esto ocurre cuando hay múltiples caminos para
   eliminar en cascada registros relacionados.

3. **Diferencias en dialectos SQL**: Existen diferencias en la sintaxis SQL entre MySQL y SQL Server que afectan la
   creación de tablas, índices y restricciones.

## Soluciones implementadas

### 1. Modificación de modelos SQLAlchemy

Se modificaron los modelos SQLAlchemy para garantizar la compatibilidad con ambos sistemas de gestión de bases de datos:

- Se reemplazó `ondelete="RESTRICT"` con `ondelete="NO ACTION"` en todas las relaciones de clave foránea.
- Se modificaron las relaciones para evitar ciclos o múltiples rutas en cascada, especialmente en las relaciones entre
  `Usuario`, `Pedido` y `LocalizacionPedido`.

Ejemplo de cambio:

```python
from sqlalchemy import Column, Integer, ForeignKey

# Antes
usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

# Después
usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="NO ACTION", onupdate="CASCADE"), nullable=False)
```

### 2. Implementación de utilidades para manejar dialectos diferentes

Se creó un módulo `app/db/dialect_utils.py` que proporciona utilidades para manejar diferentes dialectos de bases de
datos:

- `get_database_dialect()`: Detecta el dialecto de la base de datos a partir de la URL de conexión.
- `configure_dialect_specific_options(engine)`: Configura opciones específicas del dialecto para el motor de base de
  datos.
- `get_compatible_foreign_key_options(ondelete, onupdate)`: Devuelve opciones de clave foránea compatibles con ambos
  dialectos.

### 3. Modificación de la configuración de la base de datos

Se modificó el archivo `app/db/database.py` para utilizar las utilidades de dialecto y configurar opciones específicas
del dialecto al crear el motor de base de datos.

## Recomendaciones para el futuro

1. **Usar `NO ACTION` en lugar de `RESTRICT`**: Siempre usar `ondelete="NO ACTION"` en lugar de `ondelete="RESTRICT"`
   para garantizar la compatibilidad con SQL Server.

2. **Evitar ciclos o múltiples rutas en cascada**: Diseñar las relaciones de clave foránea de manera que no haya ciclos
   o múltiples rutas en cascada. Esto se puede lograr usando `ondelete="NO ACTION"` en algunas relaciones.

3. **Utilizar las utilidades de dialecto**: Utilizar las funciones proporcionadas en `app/db/dialect_utils.py` para
   manejar diferencias entre dialectos.

4. **Probar en ambos sistemas de gestión de bases de datos**: Asegurarse de probar la aplicación tanto con MySQL como
   con SQL Server para detectar problemas de compatibilidad temprano.

5. **Documentar diferencias específicas**: Mantener una documentación actualizada de las diferencias específicas entre
   MySQL y SQL Server que afectan al proyecto.

## Ejemplo de uso de las utilidades de dialecto

```python
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_base
from app.db.dialect_utils import get_compatible_foreign_key_options

# Crear base declarativa
Base = declarative_base()


# En un modelo SQLAlchemy
class MiModelo(Base):
    __tablename__ = "mi_tabla"

    id = Column(Integer, primary_key=True)

    # Usar get_compatible_foreign_key_options para obtener opciones compatibles
    otra_tabla_id = Column(
        Integer,
        ForeignKey(
            "otra_tabla.id",
            **get_compatible_foreign_key_options(ondelete="RESTRICT", onupdate="CASCADE")
        ),
        nullable=False
    )
```

Este enfoque garantiza que las opciones de clave foránea sean compatibles con ambos sistemas de gestión de bases de
datos.
