# app.py

# Sistema de Gestión de base de datos para un comercio online de velas (Amaluz)
# Copyright (C) 2025 David Javier Toscano Rico
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública General de GNU según lo publicado por
# la Free Software Foundation, ya sea la versión 3 de la Licencia, o
# (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
# COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Vea la
# Licencia Pública General de GNU para más detalles.
from flask import Flask
import pymysql
from app.core.config import config
from app.models import init_db
from app.routes import amaluz_routes

# Instala el controlador MySQLdb para pymysql
pymysql.install_as_MySQLdb()


# Carga las variables de entorno desde un archivo .env
def create_app():
    """
    Crea y configura una instancia de la aplicación Flask.

    Returns:
        Flask: La aplicación Flask configurada.
    """
    flask_app = Flask(__name__)

    # Obtiene las credenciales de la base de datos desde las variables de entorno
    db_url = config.AMALUZ_DATABASE_URL

    # Configura la conexión a la base de datos
    connection_params = f'{db_url}'
    connection_args = {'ssl': {'ssl-mode': 'disabled'}, 'auth_plugin': 'mysql_native_password'}

    # Configura las URIs de las bases de datos
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'{connection_params}/amaluz?charset=utf8mb4'
    flask_app.config['SQLALCHEMY_BINDS'] = {
        'amaluz': f'{connection_params}/amaluz?charset=utf8mb4'
    }
    flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': connection_args
    }
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa la base de datos
    init_db(flask_app)

    # Registra los blueprints con prefijos de URL
    flask_app.register_blueprint(amaluz_routes.bp, url_prefix='/api/amaluz')

    return flask_app


# Crea una instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecuta la aplicación en modo de depuración
    app.run(debug=True)
