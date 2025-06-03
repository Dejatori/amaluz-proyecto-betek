"""
Módulo para generación de datos de prueba relacionados con usuarios.
Contiene funciones para crear y actualizar usuarios en la base de datos.
"""

import random
import logging

from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.core.ai_generators import determinar_genero_persona
from app.core.security import get_contrasena_hash

from app.models.usuario import Usuario, EstadoUsuarioEnum, TipoUsuarioEnum, GeneroEnum

from app.db.data_generation.utils import sanear_string_para_correo
from app.db.data_generation.utils_datetime import generar_fecha_secuencial

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

# Constantes de configuración de usuarios
NUM_ADMINS_FIJOS = 5
NUM_VENDEDORES_DEFAULT = 10
NUM_PRIMEROS_CLIENTES_ESPECIALES = 10

# Fechas límite para administradores y vendedores
ADMIN_VENDEDOR_START_DATE = datetime(2022, 1, 1, 8, 5, 0)
ADMIN_VENDEDOR_END_DATE = datetime(2022, 1, 3, 20, 0, 0)

# Fechas límite para los primeros 10 clientes
PRIMEROS_CLIENTES_START_DATE = datetime(2022, 1, 18)
PRIMEROS_CLIENTES_END_DATE = datetime(2022, 1, 25)

# Límite global para la fecha de registro de usuarios
USER_END_DATE_LIMIT = datetime(2025, 5, 5, 20, 0, 0)

free_email_domain = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
]


def _create_admins(
    db: Session,
    count: int,
    correos_usados: set,
    telefonos_usados: set,
    total_admin_vendedores_en_rango_fecha: int,
) -> list[Usuario]:
    """Crea usuarios administradores."""
    admins = []
    admin_data = [
        {
            "nombre": "David Toscano",
            "correo": "david_toscano@amaluz.com",
            "genero": GeneroEnum.Masculino,
            "fecha_nacimiento": datetime(2000, 3, 7).date(),
        },
        {
            "nombre": "Andrea Bernal",
            "correo": "andrea_bernal@amaluz.com",
            "genero": GeneroEnum.Femenino,
            "fecha_nacimiento": fake.date_of_birth(minimum_age=25, maximum_age=40),
        },
        {
            "nombre": "Miguel Angel",
            "correo": "miguel_angel@amaluz.com",
            "genero": GeneroEnum.Masculino,
            "fecha_nacimiento": fake.date_of_birth(minimum_age=25, maximum_age=40),
        },
        {
            "nombre": "Manuela Solis",
            "correo": "manuela_solis@amaluz.com",
            "genero": GeneroEnum.Femenino,
            "fecha_nacimiento": fake.date_of_birth(minimum_age=25, maximum_age=40),
        },
        {
            "nombre": "Geraldine Sanchez",
            "correo": "geraldine_sanchez@amaluz.com",
            "genero": GeneroEnum.Femenino,
            "fecha_nacimiento": fake.date_of_birth(minimum_age=25, maximum_age=40),
        },
    ]

    for i in range(count):
        if i < len(admin_data):
            data = admin_data[i]
            nombre_completo = data["nombre"]
            correo = data["correo"]
            genero_seleccionado = data["genero"]
            fecha_nacimiento = data["fecha_nacimiento"]
            if correo in correos_usados:
                logger.warning(
                    f"Correo de admin fijo {correo} ya estaba en correos_usados. Esto no debería pasar si se llama primero."
                )
            correos_usados.add(correo)
        else:  # Si se piden más admins que los fijos, se generan aleatorios
            nombre_completo = fake.name()
            correo_base = sanear_string_para_correo(nombre_completo)
            correo = f"{correo_base}@amaluz.com"
            num_intento = 1
            while correo in correos_usados:
                correo = f"{correo_base}{num_intento}@amaluz.com"
                num_intento += 1
            correos_usados.add(correo)
            genero_seleccionado = _determinar_genero(nombre_completo)
            fecha_nacimiento = fake.date_of_birth(minimum_age=25, maximum_age=50)

        while True:
            telefono = fake.numerify(text="3##########")
            if telefono not in telefonos_usados:
                telefonos_usados.add(telefono)
                break

        fecha_creacion_aleatoria = generar_fecha_secuencial(
            fecha_inicio_rango=ADMIN_VENDEDOR_START_DATE,
            fecha_fin_rango=ADMIN_VENDEDOR_END_DATE,
            total_elementos=total_admin_vendedores_en_rango_fecha,
            indice_actual=i,
        )

        admin = Usuario(
            nombre=nombre_completo,
            correo=correo,
            contrasena=get_contrasena_hash(
                fake.password(
                    length=12,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                )
            ),
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero_seleccionado,
            tipo_usuario=TipoUsuarioEnum.Administrador,
            estado=EstadoUsuarioEnum.Activo,
            fecha_registro=fecha_creacion_aleatoria,
            fecha_actualizacion=fecha_creacion_aleatoria,
        )
        admins.append(admin)
    return admins


def _create_empleados(
    db: Session,
    count: int,
    correos_usados: set,
    telefonos_usados: set,
    indice_inicio_rango_fecha: int,
    total_admin_vendedores_en_rango_fecha: int,
) -> list[Usuario]:
    """Crea usuarios empleados (vendedores)."""
    empleados = []
    for i in range(count):
        nombre_completo = fake.name()
        correo_base = sanear_string_para_correo(nombre_completo)
        correo = f"{correo_base}@amaluz.com"
        num_intento = 1
        while correo in correos_usados:
            correo = f"{correo_base}{num_intento}@amaluz.com"
            num_intento += 1
        correos_usados.add(correo)

        while True:
            telefono = fake.numerify(text="3##########")
            if telefono not in telefonos_usados:
                telefonos_usados.add(telefono)
                break

        genero_seleccionado = _determinar_genero(nombre_completo)
        fecha_nacimiento = fake.date_of_birth(minimum_age=20, maximum_age=55)

        fecha_creacion_aleatoria = generar_fecha_secuencial(
            fecha_inicio_rango=ADMIN_VENDEDOR_START_DATE,
            fecha_fin_rango=ADMIN_VENDEDOR_END_DATE,
            total_elementos=total_admin_vendedores_en_rango_fecha,
            indice_actual=indice_inicio_rango_fecha + i,
        )

        empleado = Usuario(
            nombre=nombre_completo,
            correo=correo,
            contrasena=get_contrasena_hash(
                fake.password(
                    length=12,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                )
            ),
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero_seleccionado,
            tipo_usuario=TipoUsuarioEnum.Vendedor,
            estado=EstadoUsuarioEnum.Activo,
            fecha_registro=fecha_creacion_aleatoria,
            fecha_actualizacion=fecha_creacion_aleatoria,
        )
        empleados.append(empleado)
    return empleados


def _create_clientes(
    db: Session,
    count: int,
    correos_usados: set,
    telefonos_usados: set,
    num_primeros_especiales: int,
) -> list[Usuario]:
    """Crea usuarios clientes."""
    clientes = []
    primeros_clientes_count_local = 0

    # --- Lógica de Lotes para "El resto de clientes" (después de los especiales) ---
    lotes_config = []
    clientes_para_lotes_total = count - num_primeros_especiales

    if clientes_para_lotes_total > 0:
        fecha_inicio_global_lotes = PRIMEROS_CLIENTES_END_DATE + timedelta(
            microseconds=1
        )  # Iniciar justo después
        fecha_fin_global_lotes = USER_END_DATE_LIMIT
        duracion_total_disponible_para_lotes = (
            fecha_fin_global_lotes - fecha_inicio_global_lotes
        )

        if duracion_total_disponible_para_lotes.total_seconds() < 1:
            logger.warning(
                "No hay duración disponible para lotes de clientes. Se asignarán fechas al límite."
            )
            # Asegurar que al menos haya un delta mínimo si las fechas son iguales o invertidas
            fecha_fin_global_lotes = fecha_inicio_global_lotes + timedelta(
                days=max(
                    1,
                    (
                        clientes_para_lotes_total // 1000
                        if clientes_para_lotes_total // 1000 > 0
                        else 1
                    ),
                )
            )
            duracion_total_disponible_para_lotes = (
                fecha_fin_global_lotes - fecha_inicio_global_lotes
            )

        min_lotes = 2  # Siempre al menos dos lotes si hay clientes para lotes
        max_lotes_sugerido = 7
        if clientes_para_lotes_total < 20:
            max_lotes_sugerido = max(
                1,
                (
                    clientes_para_lotes_total // 5
                    if clientes_para_lotes_total // 5 > 0
                    else 1
                ),
            )
        elif clientes_para_lotes_total < 50:
            max_lotes_sugerido = max(
                1,
                (
                    clientes_para_lotes_total // 10
                    if clientes_para_lotes_total // 10 > 0
                    else 1
                ),
            )

        num_lotes_objetivo = random.randint(
            min_lotes, max(min_lotes, max_lotes_sugerido)
        )
        num_lotes_objetivo = min(num_lotes_objetivo, clientes_para_lotes_total)

        tamanios_finales_lotes = []
        if num_lotes_objetivo > 0:
            if num_lotes_objetivo == 1:
                tamanios_finales_lotes = [clientes_para_lotes_total]
            else:
                puntos_de_division = sorted(
                    random.sample(
                        range(1, clientes_para_lotes_total), num_lotes_objetivo - 1
                    )
                )
                ultimo_corte = 0
                for corte_val in puntos_de_division:
                    tamanios_finales_lotes.append(corte_val - ultimo_corte)
                    ultimo_corte = corte_val
                tamanios_finales_lotes.append(clientes_para_lotes_total - ultimo_corte)
                tamanios_finales_lotes = [t for t in tamanios_finales_lotes if t > 0]
                current_sum = sum(tamanios_finales_lotes)
                if (
                    current_sum != clientes_para_lotes_total and tamanios_finales_lotes
                ):  # Reajuste si es necesario
                    diff = clientes_para_lotes_total - current_sum
                    tamanios_finales_lotes[-1] += diff
                tamanios_finales_lotes = [t for t in tamanios_finales_lotes if t > 0]

        fecha_cursor_lote_actual = fecha_inicio_global_lotes
        clientes_acumulados_en_lotes = 0

        for i_lote, tamanio_del_lote in enumerate(tamanios_finales_lotes):
            if tamanio_del_lote <= 0:
                continue
            fecha_inicio_este_lote = fecha_cursor_lote_actual
            if i_lote == len(tamanios_finales_lotes) - 1:
                fecha_fin_este_lote = fecha_fin_global_lotes
            else:
                proporcion_clientes_lote = (
                    tamanio_del_lote / clientes_para_lotes_total
                    if clientes_para_lotes_total > 0
                    else 0
                )
                delta_tiempo_lote = (
                    duracion_total_disponible_para_lotes * proporcion_clientes_lote
                )
                fecha_fin_este_lote = fecha_inicio_este_lote + delta_tiempo_lote

            fecha_fin_este_lote = min(fecha_fin_este_lote, fecha_fin_global_lotes)
            if fecha_fin_este_lote < fecha_inicio_este_lote:
                fecha_fin_este_lote = fecha_inicio_este_lote + timedelta(
                    days=max(
                        1, tamanio_del_lote // 100 if tamanio_del_lote // 100 > 0 else 1
                    ),
                    microseconds=1,
                )
                fecha_fin_este_lote = min(fecha_fin_este_lote, fecha_fin_global_lotes)

            lotes_config.append(
                {
                    "tamaño": tamanio_del_lote,
                    "fecha_inicio": fecha_inicio_este_lote,
                    "fecha_fin": fecha_fin_este_lote,
                    "offset_clientes_en_lote_base": clientes_acumulados_en_lotes,  # Indice relativo al inicio de "clientes para lotes"
                }
            )
            clientes_acumulados_en_lotes += tamanio_del_lote
            fecha_cursor_lote_actual = fecha_fin_este_lote
            if (
                i_lote < len(tamanios_finales_lotes) - 1
                and fecha_cursor_lote_actual < fecha_fin_global_lotes
            ):
                fecha_cursor_lote_actual = fecha_cursor_lote_actual + timedelta(
                    microseconds=1
                )
                if fecha_cursor_lote_actual > fecha_fin_global_lotes:
                    fecha_cursor_lote_actual = fecha_fin_global_lotes

        logger.info(
            f"Configuración de lotes para clientes restantes: {len(lotes_config)} lotes generados."
        )
        for idx, lote_conf in enumerate(lotes_config):
            logger.debug(
                f"Lote Clientes {idx+1}: {lote_conf['tamaño']} clientes, "
                f"de {lote_conf['fecha_inicio']} a {lote_conf['fecha_fin']}"
            )

    for i in range(count):  # Itera sobre el total de clientes a crear en esta función
        while True:
            nombre_completo = fake.name()
            correo_base = sanear_string_para_correo(nombre_completo)
            dominio = random.choice(free_email_domain)
            correo = f"{correo_base}@{dominio}"
            if correo not in correos_usados:
                correos_usados.add(correo)
                break
            else:
                correo_unico_alt = fake.unique.email()
                if correo_unico_alt not in correos_usados:
                    correo = correo_unico_alt
                    correos_usados.add(correo)
                    break

        while True:
            telefono = fake.numerify(text="3##########")
            if telefono not in telefonos_usados:
                telefonos_usados.add(telefono)
                break

        genero_seleccionado = _determinar_genero(nombre_completo)
        fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=80)

        if i < num_primeros_especiales:  # Primeros clientes especiales
            fecha_creacion_aleatoria = generar_fecha_secuencial(
                fecha_inicio_rango=PRIMEROS_CLIENTES_START_DATE,
                fecha_fin_rango=PRIMEROS_CLIENTES_END_DATE,
                total_elementos=num_primeros_especiales,
                indice_actual=primeros_clientes_count_local,
            )
            primeros_clientes_count_local += 1
        else:  # Resto de clientes (usando la lógica de lotes)
            # El índice 'i' es global para esta función _create_clientes.
            # Necesitamos el índice relativo a los "clientes para lotes".
            indice_cliente_para_lotes = i - num_primeros_especiales

            lote_actual_info = None
            for lote_info_item in reversed(lotes_config):
                if (
                    indice_cliente_para_lotes
                    >= lote_info_item["offset_clientes_en_lote_base"]
                ):
                    lote_actual_info = lote_info_item
                    break

            if lote_actual_info:
                indice_en_lote_actual = (
                    indice_cliente_para_lotes
                    - lote_actual_info["offset_clientes_en_lote_base"]
                )
                fecha_creacion_aleatoria = generar_fecha_secuencial(
                    fecha_inicio_rango=lote_actual_info["fecha_inicio"],
                    fecha_fin_rango=lote_actual_info["fecha_fin"],
                    total_elementos=lote_actual_info["tamaño"],
                    indice_actual=indice_en_lote_actual,
                )
            else:  # Fallback si no se encuentra lote (no debería pasar si hay clientes para lotes)
                logger.warning(
                    f"Cliente {i}: Sin configuración de lotes aplicable, usando fecha aleatoria simple dentro del rango global de clientes."
                )
                start_fallback = PRIMEROS_CLIENTES_END_DATE + timedelta(microseconds=1)
                end_fallback = USER_END_DATE_LIMIT
                if start_fallback >= end_fallback:  # Asegurar que el rango sea válido
                    end_fallback = start_fallback + timedelta(days=1)
                fecha_creacion_aleatoria = fake.date_time_between_dates(
                    datetime_start=start_fallback, datetime_end=end_fallback
                )

        cliente = Usuario(
            nombre=nombre_completo,
            correo=correo,
            contrasena=get_contrasena_hash(
                fake.password(
                    length=10,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                )
            ),
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero_seleccionado,
            tipo_usuario=TipoUsuarioEnum.Cliente,
            estado=EstadoUsuarioEnum.Sin_confirmar,  # Los clientes empiezan sin confirmar
            fecha_registro=fecha_creacion_aleatoria,
            fecha_actualizacion=fecha_creacion_aleatoria,
        )
        clientes.append(cliente)
    return clientes


def _determinar_genero(nombre: str) -> GeneroEnum:
    """
    Determina el género de un nombre dado.
    Utiliza una lógica simple basada en nombres comunes en español.
    """
    primer_nombre = nombre.split()[0].lower()
    genero = determinar_genero_persona(primer_nombre)
    return (
        GeneroEnum(genero)
        if genero in GeneroEnum._value2member_map_
        else random.choice(list(GeneroEnum))
    )


def create_users(db: Session, total_count: int) -> list[Usuario]:
    """
    Crea usuarios de prueba (administradores, empleados, clientes) en la base de datos.
    Si ya existen administradores o vendedores, intentará completar hasta
    NUM_ADMINS_FIJOS y NUM_VENDEDORES_DEFAULT respectivamente,
    y el resto del total_count se usará para crear clientes.
    Si los admins y vendedores fijos/default ya existen, total_count se usará íntegramente para clientes.

    Args:
        db: Sesión de base de datos
        total_count: Número total de NUEVOS usuarios a crear en esta ejecución.

    Returns:
        Lista de todos los usuarios creados en ESTA EJECUCIÓN.
    """
    all_new_users = []

    # Obtener datos de usuarios existentes para evitar duplicados y contar tipos
    existing_db_users = db.query(
        Usuario.correo, Usuario.telefono, Usuario.tipo_usuario
    ).all()
    correos_usados = {user.correo for user in existing_db_users if user.correo}
    telefonos_usados = {user.telefono for user in existing_db_users if user.telefono}

    conteo_admins_existentes = sum(
        1
        for user in existing_db_users
        if user.tipo_usuario == TipoUsuarioEnum.Administrador
    )
    conteo_vendedores_existentes = sum(
        1 for user in existing_db_users if user.tipo_usuario == TipoUsuarioEnum.Vendedor
    )

    logger.info(
        f"Usuarios existentes: {len(existing_db_users)} (Admins: {conteo_admins_existentes}, Vendedores: {conteo_vendedores_existentes})."
    )
    logger.info(f"Se intentarán crear {total_count} nuevos usuarios.")

    num_admins_a_crear = 0
    num_vendedores_a_crear = 0
    num_clientes_a_crear = 0

    usuarios_restantes_por_crear = total_count

    # 1. Determinar cuántos administradores nuevos crear
    if usuarios_restantes_por_crear > 0:
        admins_faltantes_para_fijos = max(
            0, NUM_ADMINS_FIJOS - conteo_admins_existentes
        )
        num_admins_a_crear = min(
            admins_faltantes_para_fijos, usuarios_restantes_por_crear
        )
        if num_admins_a_crear > 0:
            usuarios_restantes_por_crear -= num_admins_a_crear

    # 2. Determinar cuántos vendedores nuevos crear
    if usuarios_restantes_por_crear > 0:
        vendedores_faltantes_para_default = max(
            0, NUM_VENDEDORES_DEFAULT - conteo_vendedores_existentes
        )
        num_vendedores_a_crear = min(
            vendedores_faltantes_para_default, usuarios_restantes_por_crear
        )
        if num_vendedores_a_crear > 0:
            usuarios_restantes_por_crear -= num_vendedores_a_crear

    # 3. El resto de usuarios a crear serán clientes
    num_clientes_a_crear = usuarios_restantes_por_crear

    # Total de admins y vendedores NUEVOS que se crearán en esta tanda (para la distribución de fechas)
    total_nuevos_admin_vendedores_en_rango_fecha = (
        num_admins_a_crear + num_vendedores_a_crear
    )

    if num_admins_a_crear > 0:
        logger.info(f"Creando {num_admins_a_crear} nuevos administradores...")
        admins = _create_admins(
            db,
            num_admins_a_crear,
            correos_usados,
            telefonos_usados,
            total_nuevos_admin_vendedores_en_rango_fecha,
        )
        all_new_users.extend(admins)
    else:
        logger.info(
            "No se crearán nuevos administradores (ya existen suficientes o no hay cupo en total_count)."
        )

    if num_vendedores_a_crear > 0:
        logger.info(
            f"Creando {num_vendedores_a_crear} nuevos empleados (vendedores)..."
        )
        # El índice de inicio para los vendedores en el rango de fechas compartido es después de los admins NUEVOS creados en ESTA tanda.
        empleados = _create_empleados(
            db,
            num_vendedores_a_crear,
            correos_usados,
            telefonos_usados,
            indice_inicio_rango_fecha=num_admins_a_crear,  # Solo cuenta los admins creados AHORA
            total_admin_vendedores_en_rango_fecha=total_nuevos_admin_vendedores_en_rango_fecha,
        )
        all_new_users.extend(empleados)
    else:
        logger.info(
            "No se crearán nuevos vendedores (ya existen suficientes o no hay cupo en total_count)."
        )

    if num_clientes_a_crear > 0:
        logger.info(f"Creando {num_clientes_a_crear} nuevos clientes...")
        # Determinar cuántos de estos clientes son "primeros especiales" para ESTA TANDA de creación
        num_primeros_especiales_para_clientes = min(
            num_clientes_a_crear, NUM_PRIMEROS_CLIENTES_ESPECIALES
        )

        clientes = _create_clientes(
            db,
            num_clientes_a_crear,
            correos_usados,
            telefonos_usados,
            num_primeros_especiales_para_clientes,
        )
        all_new_users.extend(clientes)
    else:
        logger.info(
            "No se crearán nuevos clientes (no hay cupo en total_count después de admins/vendedores)."
        )

    if all_new_users:
        try:
            db.add_all(all_new_users)
            db.commit()
            logger.info(
                f"Total de {len(all_new_users)} NUEVOS usuarios creados y guardados en la base de datos."
            )
            for (
                user
            ) in (
                all_new_users
            ):  # Para asegurar que los IDs están disponibles si se necesitan inmediatamente
                db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error al guardar nuevos usuarios: {e}", exc_info=True)
            return []  # Retorna lista vacía en caso de error de commit
    else:
        logger.info("No se crearon nuevos usuarios en esta ejecución.")

    return all_new_users


def update_user_estado(db: Session, num_sin_confirmar_a_dejar: int):
    """
    Actualiza el estado de los usuarios de 'Sin confirmar' a 'Activo'.
    Deja un número específico de usuarios como 'Sin confirmar'.
    Actualiza la fecha_actualizacion para los usuarios modificados.

    Args:
        db: Sesión de base de datos
        num_sin_confirmar_a_dejar: Número de usuarios a dejar como 'Sin confirmar'
    """
    usuarios_sin_confirmar = (
        db.query(Usuario)
        .filter(Usuario.estado == EstadoUsuarioEnum.Sin_confirmar)
        .all()
    )

    if not usuarios_sin_confirmar:
        logger.info("No hay usuarios con estado 'Sin confirmar' para actualizar.")
        return

    num_total_sin_confirmar = len(usuarios_sin_confirmar)
    logger.info(f"Encontrados {num_total_sin_confirmar} usuarios 'Sin confirmar'.")

    if num_total_sin_confirmar <= num_sin_confirmar_a_dejar:
        logger.info(
            f"El número de usuarios 'Sin confirmar' ({num_total_sin_confirmar}) "
            f"es menor o igual al número a dejar ({num_sin_confirmar_a_dejar}). No se realizarán cambios."
        )
        return

    # Barajar la lista para seleccionar aleatoriamente cuáles dejar
    random.shuffle(usuarios_sin_confirmar)

    usuarios_a_actualizar = usuarios_sin_confirmar[num_sin_confirmar_a_dejar:]
    # Los primeros 'num_sin_confirmar_a_dejar' usuarios en la lista barajada se quedarán como están.

    actualizados_count = 0
    for usuario in usuarios_a_actualizar:
        usuario.estado = EstadoUsuarioEnum.Activo

        # 80% de los usuarios confirman entre 2 y 10 minutos, 20% entre 1 y 2 días
        if isinstance(usuario.fecha_registro, datetime):
            if random.random() < 0.8:  # 80% confirman rápido
                minutos_adicionales = random.randint(2, 10)
                nueva_fecha_actualizacion = usuario.fecha_registro + timedelta(
                    minutes=minutos_adicionales
                )
            else:  # 20% tardan más
                dias_adicionales = random.randint(1, 2)
                minutos_adicionales = random.randint(0, 59)
                nueva_fecha_actualizacion = usuario.fecha_registro + timedelta(
                    days=dias_adicionales, minutes=minutos_adicionales
                )

            usuario.fecha_actualizacion = nueva_fecha_actualizacion
            actualizados_count += 1

    if actualizados_count > 0:
        try:
            db.commit()
            logger.info(
                f"Actualizados {actualizados_count} usuarios de 'Sin confirmar' a 'Activo'."
            )
            logger.info(
                f"Se dejaron {num_sin_confirmar_a_dejar} usuarios con estado 'Sin confirmar'."
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error al actualizar estado de usuarios: {e}")
            raise
    else:
        logger.info("No se actualizaron usuarios (después de la selección aleatoria).")


def get_usuarios_activos_clientes(db: Session):
    """
    Obtiene una lista de usuarios activos que son clientes.

    Args:
        db: Sesión de base de datos

    Returns:
        Lista de usuarios activos que son clientes
    """
    usuarios_activos_clientes = (
        db.query(Usuario)
        .filter(
            Usuario.estado == EstadoUsuarioEnum.Activo,
            Usuario.tipo_usuario == TipoUsuarioEnum.Cliente,
        )
        .all()
    )
    return usuarios_activos_clientes
