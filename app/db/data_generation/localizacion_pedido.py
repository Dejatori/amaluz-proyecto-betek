"""
Módulo para generación de datos de prueba relacionados con localizaciones de pedido.
Contiene funciones para crear localizaciones en la base de datos.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.data_generation.utils_datetime import (
    get_random_datetime_in_range,
    SIMULATION_END_DATE
)
from app.models.localizacion_pedido import LocalizacionPedido
from app.models.usuario import Usuario
from app.core.ai_generators import (
    generate_descripcion_localizacion_ia,
    generate_notas_entrega_ia,
)

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

# Departamentos, ciudades y códigos postales de Colombia
departamentos_y_ciudades: Dict[str, List[Dict[str, str]]] = {
    "Antioquia": [
        {"ciudad": "Medellín", "codigo_postal": "050001"},
        {"ciudad": "Envigado", "codigo_postal": "055422"},
        {"ciudad": "Bello", "codigo_postal": "051050"},
        {"ciudad": "Itagüí", "codigo_postal": "055413"},
        {"ciudad": "Apartadó", "codigo_postal": "057040"},
        {"ciudad": "Turbo", "codigo_postal": "057050"},
    ],
    "Cundinamarca": [
        {"ciudad": "Bogotá", "codigo_postal": "110111"},
        {"ciudad": "Soacha", "codigo_postal": "250051"},
        {"ciudad": "Chía", "codigo_postal": "250001"},
        {"ciudad": "Cajicá", "codigo_postal": "250220"},
    ],
    "Valle del Cauca": [
        {"ciudad": "Cali", "codigo_postal": "760001"},
        {"ciudad": "Palmira", "codigo_postal": "763531"},
        {"ciudad": "Buenaventura", "codigo_postal": "764501"},
        {"ciudad": "Tuluá", "codigo_postal": "763022"},
    ],
    "Atlántico": [
        {"ciudad": "Barranquilla", "codigo_postal": "080001"},
        {"ciudad": "Soledad", "codigo_postal": "083001"},
        {"ciudad": "Malambo", "codigo_postal": "083021"},
        {"ciudad": "Puerto Colombia", "codigo_postal": "081001"},
    ],
    "Santander": [
        {"ciudad": "Bucaramanga", "codigo_postal": "680001"},
        {"ciudad": "Floridablanca", "codigo_postal": "681001"},
        {"ciudad": "Barrancabermeja", "codigo_postal": "687031"},
        {"ciudad": "Girón", "codigo_postal": "687541"},
    ],
    "Bolívar": [
        {"ciudad": "Cartagena", "codigo_postal": "130001"},
        {"ciudad": "Magangué", "codigo_postal": "132501"},
        {"ciudad": "Turbaco", "codigo_postal": "131001"},
        {"ciudad": "Arjona", "codigo_postal": "130501"},
    ],
    "Córdoba": [
        {"ciudad": "Montería", "codigo_postal": "230001"},
        {"ciudad": "Lorica", "codigo_postal": "234501"},
        {"ciudad": "Cereté", "codigo_postal": "233501"},
        {"ciudad": "Sahagún", "codigo_postal": "232501"},
    ],
    "Norte de Santander": [
        {"ciudad": "Cúcuta", "codigo_postal": "540001"},
        {"ciudad": "Ocaña", "codigo_postal": "546551"},
        {"ciudad": "Pamplona", "codigo_postal": "543050"},
        {"ciudad": "Los Patios", "codigo_postal": "541010"},
    ],
    "Nariño": [
        {"ciudad": "Pasto", "codigo_postal": "520001"},
        {"ciudad": "Tumaco", "codigo_postal": "528501"},
        {"ciudad": "Ipiales", "codigo_postal": "524060"},
        {"ciudad": "La Unión", "codigo_postal": "524001"}
    ],
    "Caldas": [
        {"ciudad": "Manizales", "codigo_postal": "170001"},
        {"ciudad": "Villamaría", "codigo_postal": "170002"},
        {"ciudad": "Chinchiná", "codigo_postal": "176020"},
        {"ciudad": "Neira", "codigo_postal": "175020"}
    ],
    "Quindío": [
        {"ciudad": "Armenia", "codigo_postal": "630001"},
        {"ciudad": "Montenegro", "codigo_postal": "633001"},
        {"ciudad": "Circasia", "codigo_postal": "631001"},
        {"ciudad": "Salento", "codigo_postal": "631020"}
    ],
    "Risaralda": [
        {"ciudad": "Pereira", "codigo_postal": "660001"},
        {"ciudad": "Dosquebradas", "codigo_postal": "661001"},
        {"ciudad": "Santa Rosa de Cabal", "codigo_postal": "663001"},
        {"ciudad": "La Virginia", "codigo_postal": "662001"}
    ],
    "Tolima": [
        {"ciudad": "Ibagué", "codigo_postal": "730001"},
        {"ciudad": "Espinal", "codigo_postal": "733501"},
        {"ciudad": "Melgar", "codigo_postal": "734001"},
        {"ciudad": "Líbano", "codigo_postal": "731501"}
    ],
    "Huila": [
        {"ciudad": "Neiva", "codigo_postal": "410001"},
        {"ciudad": "Pitalito", "codigo_postal": "417030"},
        {"ciudad": "La Plata", "codigo_postal": "415060"},
        {"ciudad": "Garzón", "codigo_postal": "414001"}
    ],
    "Cauca": [
        {"ciudad": "Popayán", "codigo_postal": "190001"},
        {"ciudad": "Santander de Quilichao", "codigo_postal": "191030"},
        {"ciudad": "El Bordo", "codigo_postal": "195001"},
    ],
    "Caquetá": [
        {"ciudad": "Florencia", "codigo_postal": "180001"},
        {"ciudad": "San Vicente del Caguán", "codigo_postal": "182001"},
        {"ciudad": "La Montañita", "codigo_postal": "183001"}
    ],
    "Meta": [
        {"ciudad": "Villavicencio", "codigo_postal": "500001"},
        {"ciudad": "Acacías", "codigo_postal": "501001"},
        {"ciudad": "Cumaral", "codigo_postal": "501501"},
        {"ciudad": "Restrepo", "codigo_postal": "501020"}
    ],
    "Casanare": [
        {"ciudad": "Yopal", "codigo_postal": "850001"},
        {"ciudad": "Aguazul", "codigo_postal": "851001"},
        {"ciudad": "Támara", "codigo_postal": "852001"},
        {"ciudad": "Hato Corozal", "codigo_postal": "853001"}
    ],
    "Arauca": [
        {"ciudad": "Arauca", "codigo_postal": "810001"},
        {"ciudad": "Saravena", "codigo_postal": "813001"},
        {"ciudad": "Tame", "codigo_postal": "814001"},
        {"ciudad": "Fortul", "codigo_postal": "812001"}
    ],
    "Vaupés": [
        {"ciudad": "Mitú", "codigo_postal": "970001"},
        {"ciudad": "Carurú", "codigo_postal": "971001"},
        {"ciudad": "Papunaua", "codigo_postal": "972001"},
        {"ciudad": "Taraira", "codigo_postal": "973001"}
    ],
    "Guaviare": [
        {"ciudad": "San José del Guaviare", "codigo_postal": "950001"},
        {"ciudad": "Calamar", "codigo_postal": "951001"},
        {"ciudad": "Miraflores", "codigo_postal": "952001"},
        {"ciudad": "El Retorno", "codigo_postal": "953001"}
    ],
    "Guainía": [
        {"ciudad": "Inírida", "codigo_postal": "940001"},
        {"ciudad": "Barranco Minas", "codigo_postal": "943001"},
        {"ciudad": "San Felipe", "codigo_postal": "944001"},
        {"ciudad": "Cacahual", "codigo_postal": "945001"}
    ],
    "Vichada": [
        {"ciudad": "Puerto Carreño", "codigo_postal": "990001"},
        {"ciudad": "La Primavera", "codigo_postal": "991001"},
        {"ciudad": "Santa Rosalía", "codigo_postal": "992001"},
        {"ciudad": "Cumaribo", "codigo_postal": "993001"}
    ],
    "Amazonas": [
        {"ciudad": "Leticia", "codigo_postal": "910001"},
        {"ciudad": "Puerto Nariño", "codigo_postal": "911001"},
        {"ciudad": "El Encanto", "codigo_postal": "912001"}
    ],
    "Cesar": [
        {"ciudad": "Valledupar", "codigo_postal": "200001"},
        {"ciudad": "Aguachica", "codigo_postal": "205001"},
        {"ciudad": "La Paz", "codigo_postal": "201001"},
        {"ciudad": "Codazzi", "codigo_postal": "202001"}
    ],
    "La Guajira": [
        {"ciudad": "Riohacha", "codigo_postal": "440001"},
        {"ciudad": "Maicao", "codigo_postal": "442001"},
        {"ciudad": "Uribia", "codigo_postal": "443001"},
        {"ciudad": "Fonseca", "codigo_postal": "444001"}
    ],
    "Sucre": [
        {"ciudad": "Sincelejo", "codigo_postal": "700001"},
        {"ciudad": "Corozal", "codigo_postal": "701001"},
        {"ciudad": "Sampués", "codigo_postal": "702001"},
        {"ciudad": "San Marcos", "codigo_postal": "703001"}
    ],
    "Putumayo": [
        {"ciudad": "Mocoa", "codigo_postal": "860001"},
        {"ciudad": "Puerto Asís", "codigo_postal": "861001"},
        {"ciudad": "Orito", "codigo_postal": "862001"},
        {"ciudad": "San Francisco", "codigo_postal": "863001"}
    ],
    "Chocó": [
        {"ciudad": "Quibdó", "codigo_postal": "270001"},
        {"ciudad": "Carmen del Darién", "codigo_postal": "271001"}
    ],
}

def create_localizacion_for_user(
        db: Session,
        usuario: Usuario,
        max_allowable_date: datetime,
        fecha_minima: Optional[datetime] = None
) -> Optional[LocalizacionPedido]:
    """
    Crea una localización para un usuario con coherencia temporal.

    Args:
        db: Sesión de base de datos.
        usuario: Usuario para el que se crea la localización.
        max_allowable_date: Fecha máxima permitida para la localización.
        fecha_minima: Fecha mínima permitida para la localización (opcional).

    Returns:
        Objeto LocalizacionPedido creado o None si no se pudo crear.
    """
    # Buscar la última localización del usuario
    ultima_localizacion = (
        db.query(LocalizacionPedido)
        .filter(LocalizacionPedido.usuario_id == usuario.id)
        .order_by(LocalizacionPedido.fecha_registro.desc())
        .first()
    )

    # Determinar la fecha base mínima
    # Si se proporciona fecha_minima, usarla; de lo contrario, calcular basado en registros existentes
    if fecha_minima is None:
        # Comportamiento original: la fecha base mínima es la fecha de registro del usuario
        # o la fecha de la última localización + 1 segundo
        min_possible_date = usuario.fecha_registro
        if ultima_localizacion:
            min_possible_date = max(
                min_possible_date,
                ultima_localizacion.fecha_registro + timedelta(seconds=1)
            )
        # Añadir 1 día a la fecha de registro como margen de seguridad
        min_possible_date += timedelta(days=1)
    else:
        # Usar la fecha mínima proporcionada, pero verificar que sea posterior
        # a cualquier localización existente
        min_possible_date = fecha_minima
        if ultima_localizacion and ultima_localizacion.fecha_registro >= min_possible_date:
            # Si hay una localización más reciente que la fecha mínima proporcionada,
            # ajustar la fecha mínima para que sea posterior
            min_possible_date = ultima_localizacion.fecha_registro + timedelta(seconds=1)

    # Verificar que la fecha mínima no exceda la fecha máxima permitida
    if min_possible_date > max_allowable_date:
        logger.warning(
            f"max_allowable_date ({max_allowable_date}) es anterior a la fecha mínima posible "
            f"({min_possible_date}) para la localización del usuario {usuario.id}. "
            f"No se puede crear la localización."
        )
        return None

    try:
        departamento_nombre = random.choice(list(departamentos_y_ciudades.keys()))
        ciudades_del_departamento = departamentos_y_ciudades[departamento_nombre]
        ciudad_seleccionada_info = random.choice(ciudades_del_departamento)
        ciudad_nombre = ciudad_seleccionada_info["ciudad"]
        codigo_postal_seleccionado = ciudad_seleccionada_info["codigo_postal"]

        try:
            descripcion_loc = generate_descripcion_localizacion_ia()
            notas_ent = generate_notas_entrega_ia()
            # descripcion_loc = fake.sentence(nb_words=10)
            # notas_ent = fake.sentence(nb_words=15)
        except Exception as e_ia:
            logger.error(f"Error generando datos con IA para localización (usuario {usuario.id}): {e_ia}", exc_info=True)
            descripcion_loc = fake.sentence(nb_words=10)
            notas_ent = fake.sentence(nb_words=15)

        # Seleccionar una fecha aleatoria entre la mínima y máxima permitidas
        fecha_registro = get_random_datetime_in_range(min_possible_date, max_allowable_date)

        nueva_localizacion = LocalizacionPedido(
            usuario_id=usuario.id,
            direccion_1=fake.street_address(),
            direccion_2=fake.secondary_address() if random.random() > 0.7 else None,
            ciudad=ciudad_nombre,
            departamento=departamento_nombre,
            codigo_postal=codigo_postal_seleccionado,
            descripcion=descripcion_loc,
            notas_entrega=notas_ent,
            fecha_registro=fecha_registro,
            fecha_actualizacion=fecha_registro
        )

        db.add(nueva_localizacion)
        db.flush()
        return nueva_localizacion

    except SQLAlchemyError as e:
        logger.error(f"Error al crear localización para usuario {usuario.id}: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Error inesperado creando localización para usuario {usuario.id}: {e}")
        db.rollback()
        return None
