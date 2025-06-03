"""
Utilidades para manejar diferentes dialectos de bases de datos en SQLAlchemy.

Este módulo proporciona funciones y clases para manejar las diferencias entre
MySQL y SQL Server en SQLAlchemy, especialmente en lo relacionado con las
restricciones de clave foránea y la sintaxis SQL.
"""
from urllib.parse import urlparse
from app.core.config import config


def get_database_dialect():
    """
    Detecta el dialecto de la base de datos a partir de la URL de conexión.
    
    Returns:
        str: El dialecto de la base de datos ('mysql' o 'mssql').
        
    Raises:
        ValueError: Si el dialecto no es compatible.
    """
    DATABASE_URL = str(config.DATABASE_URL)
    parsed_url = urlparse(DATABASE_URL)

    if parsed_url.scheme.startswith('mysql'):
        return 'mysql'
    elif parsed_url.scheme.startswith('mssql'):
        return 'mssql'
    else:
        raise ValueError(f"Dialecto no compatible: {parsed_url.scheme}")


def get_compatible_foreign_key_options(ondelete=None, onupdate=None):
    """
    Devuelve opciones de clave foránea compatibles con ambos dialectos.
    
    Args:
        ondelete (str, optional): Acción a realizar al eliminar. Defaults to None.
        onupdate (str, optional): Acción a realizar al actualizar. Defaults to None.
        
    Returns:
        dict: Diccionario con opciones compatibles.
    """
    options = {}
    dialect = get_database_dialect()

    # Manejar ondelete
    if ondelete:
        # Para SQL Server, usar NO ACTION para evitar ciclos o múltiples rutas en cascada
        if dialect == 'mssql':
            options["ondelete"] = "NO ACTION"
        else:
            # Para MySQL, respetar la opción original, pero reemplazar RESTRICT con NO ACTION
            if ondelete.upper() == "RESTRICT":
                options["ondelete"] = "NO ACTION"
            else:
                options["ondelete"] = ondelete

    # Manejar onupdate
    if onupdate:
        # Para SQL Server, usar NO ACTION para evitar ciclos cuando sea necesario
        if dialect == 'mssql' and onupdate.upper() == "CASCADE":
            # Si estamos en una relación que podría causar ciclos, usar NO ACTION
            options["onupdate"] = "NO ACTION"
        else:
            options["onupdate"] = onupdate

    return options
