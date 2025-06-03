"""
Módulo para generación de datos de prueba relacionados con productos.
Contiene funciones para crear productos en la base de datos.
"""

import random
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Producto
from app.models.producto import (
    Producto,
    CategoriaProductoEnum,
    EstadoProductoEnum,
    FraganciaProductoEnum,
)
from app.models.proveedor import Proveedor
from app.core.ai_generators import (
    generar_nombre_producto_ia,
    generar_descripcion_producto_ia,
    generate_image_pollinations,
)
from app.db.data_generation.utils_datetime import (
    PRODUCTOS_START_DATE_LIMIT,
    PRODUCTOS_END_DATE_LIMIT,
)

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")  # Usar localización para datos más realistas


def create_productos(
    db: Session, count: int, proveedores: list[Proveedor]
) -> list[Producto]:
    """
    Crea productos de prueba en la base de datos con coherencia temporal.

    Args:
        db: Sesión de base de datos
        count: Número de productos a crear
        proveedores: Lista de proveedores para asociar con los productos

    Returns:
        Lista de productos generados
    """
    productos_creados = []
    nombres_productos_usados = set()  # Para rastrear nombres de productos únicos

    # Asegurarse de que tenemos al menos un proveedor
    if not proveedores:
        logger.warning("No hay proveedores disponibles para crear productos")
        return []

    proveedores_ordenados = sorted(proveedores, key=lambda p: p.fecha_registro)
    num_proveedores = len(proveedores_ordenados)

    # --- Inicio: Lógica de Distribución de Productos ---
    productos_por_proveedor = {p.id: 0 for p in proveedores_ordenados}

    # Paso 1: Asignar una base de productos (e.g., 1 por proveedor si count lo permite)
    productos_asignados_base = 0
    if count >= num_proveedores:
        for (
            p_id_loop
        ) in (
            productos_por_proveedor
        ):  # Usar p_id_loop para evitar conflicto con p fuera del bucle
            productos_por_proveedor[p_id_loop] = 1
        productos_asignados_base = num_proveedores
    else:
        # Menos productos que proveedores: asignar a los más antiguos
        for i in range(count):
            productos_por_proveedor[proveedores_ordenados[i].id] = 1
        productos_asignados_base = count

    productos_restantes_para_distribuir = count - productos_asignados_base

    # Paso 2: Distribuir los productos restantes proporcionalmente
    if productos_restantes_para_distribuir > 0:
        # Calcular días disponibles para cada proveedor para la ponderación
        # Usar PRODUCTOS_END_DATE_LIMIT como referencia para la "antigüedad" o "espacio disponible"
        dias_disponibles_por_proveedor = {}
        for p_loop in proveedores_ordenados:  # Usar p_loop
            # Asegurar que los días sean al menos 1 para evitar división por cero si todos están en el límite
            dias = max(1, (PRODUCTOS_END_DATE_LIMIT - p_loop.fecha_registro).days)
            dias_disponibles_por_proveedor[p_loop.id] = dias

        total_dias_ponderados = sum(dias_disponibles_por_proveedor.values())

        if total_dias_ponderados > 0:
            temp_asignaciones_proporcionales = {}
            for p_loop in proveedores_ordenados:  # Usar p_loop
                proporcion_p = (
                    dias_disponibles_por_proveedor[p_loop.id] / total_dias_ponderados
                )
                asignacion_exacta = proporcion_p * productos_restantes_para_distribuir
                temp_asignaciones_proporcionales[p_loop.id] = asignacion_exacta

            # Asignar la parte entera de la proporción
            for (
                p_id_loop,
                asignacion_exacta,
            ) in temp_asignaciones_proporcionales.items():
                productos_por_proveedor[p_id_loop] += int(asignacion_exacta)

            # Calcular cuántos faltan por asignar debido al redondeo
            total_asignado_despues_enteros = sum(productos_por_proveedor.values())
            productos_aun_restantes_redondeo = count - total_asignado_despues_enteros

            # Distribuir los restantes por redondeo (a los que tuvieron mayor fracción)
            if productos_aun_restantes_redondeo > 0:
                proveedores_ordenados_por_fraccion = sorted(
                    proveedores_ordenados,
                    key=lambda prov: temp_asignaciones_proporcionales.get(prov.id, 0)
                    - int(temp_asignaciones_proporcionales.get(prov.id, 0)),
                    reverse=True,
                )
                for i in range(productos_aun_restantes_redondeo):
                    proveedor_idx = i % num_proveedores
                    productos_por_proveedor[
                        proveedores_ordenados_por_fraccion[proveedor_idx].id
                    ] += 1
        else:
            # Fallback: si total_dias_ponderados es 0 (todos los proveedores más allá del límite), distribuir equitativamente.
            logger.warning(
                "No se pudieron calcular días ponderados para distribución proporcional. Distribuyendo restantes equitativamente."
            )
            for i in range(productos_restantes_para_distribuir):
                productos_por_proveedor[
                    proveedores_ordenados[i % num_proveedores].id
                ] += 1

    # Ajuste final para asegurar que la suma sea exactamente 'count' (por si acaso)
    suma_actual_distribucion = sum(productos_por_proveedor.values())
    diferencia_final_ajuste = count - suma_actual_distribucion
    if diferencia_final_ajuste > 0:  # Faltan productos
        for i in range(diferencia_final_ajuste):
            productos_por_proveedor[proveedores_ordenados[i % num_proveedores].id] += 1
    elif diferencia_final_ajuste < 0:  # Sobran productos
        for i in range(abs(diferencia_final_ajuste)):
            # Quitar de los proveedores con más productos, pero sin bajar del mínimo (1 si count >= num_proveedores)
            proveedor_a_quitar = sorted(
                proveedores_ordenados,
                key=lambda p: productos_por_proveedor[p.id],
                reverse=True,
            )[i % num_proveedores]
            min_productos_este_proveedor = (
                1
                if count >= num_proveedores
                and productos_por_proveedor[proveedor_a_quitar.id] > 0
                else 0
            )
            if (
                productos_por_proveedor[proveedor_a_quitar.id]
                > min_productos_este_proveedor
            ):
                productos_por_proveedor[proveedor_a_quitar.id] -= 1
            else:  # Si no se pudo quitar, intentar con el siguiente más cargado o el primero para forzar
                productos_por_proveedor[proveedores_ordenados[0].id] -= 1

    logger.info(
        f"Distribución planificada de productos por proveedor (Total: {sum(productos_por_proveedor.values())}/{count}):"
    )
    for p_id, cantidad in productos_por_proveedor.items():
        logger.info(f"Proveedor ID {p_id}: {cantidad} productos planificados")
    if sum(productos_por_proveedor.values()) != count:
        logger.critical(
            f"LA DISTRIBUCIÓN FINAL NO SUMA {count}. Suma: {sum(productos_por_proveedor.values())}. Revisar lógica."
        )
    # --- Fin: Lógica de Distribución de Productos ---

    # Inicializar la última fecha de registro global.
    if proveedores_ordenados:
        start_date_ref = proveedores_ordenados[0].fecha_registro - timedelta(seconds=1)
        ultima_fecha_registro_global = max(PRODUCTOS_START_DATE_LIMIT, start_date_ref)
    else:  # No debería ocurrir si se validó antes
        ultima_fecha_registro_global = PRODUCTOS_START_DATE_LIMIT

    fecha_limite_absoluta_productos = min(PRODUCTOS_END_DATE_LIMIT, datetime.now())
    detener_creacion_total = False
    productos_creados_proveedor_log = {p.id: 0 for p in proveedores_ordenados}

    for proveedor_actual in proveedores_ordenados:
        if detener_creacion_total:
            break

        num_productos_para_este_proveedor = productos_por_proveedor.get(
            proveedor_actual.id, 0
        )
        if num_productos_para_este_proveedor == 0:
            continue

        # --- INICIO: PRE-CHECK PARA EL PROVEEDOR ---
        # Determinar la fecha más temprana posible para el primer producto de este proveedor.
        # Debe ser después del registro del proveedor + un retraso mínimo, y después del último producto global.
        min_delay_after_provider_reg = timedelta(
            hours=1
        )  # Retraso mínimo sensato para un nuevo producto
        earliest_datetime_for_this_provider = (
            proveedor_actual.fecha_registro + min_delay_after_provider_reg
        )

        # El producto también debe venir después del último producto registrado globalmente.
        # Añadir un búfer de 1 segundo para asegurar que sea estrictamente posterior.
        next_possible_global_datetime = ultima_fecha_registro_global + timedelta(
            seconds=1
        )

        # El inicio más temprano real para el producto de este proveedor es el posterior de estos dos.
        candidate_start_datetime = max(
            earliest_datetime_for_this_provider, next_possible_global_datetime
        )

        if candidate_start_datetime >= fecha_limite_absoluta_productos:
            logger.warning(
                f"Proveedor {proveedor_actual.id} (fecha_reg: {proveedor_actual.fecha_registro}) "
                f"no puede tener productos. La fecha de inicio más temprana posible ({candidate_start_datetime}) "
                f"para su primer producto supera o iguala el límite ({fecha_limite_absoluta_productos}). "
                f"Última fecha global: {ultima_fecha_registro_global}."
            )
            continue  # Saltar al siguiente proveedor
        # --- FIN: PRE-CHECK PARA EL PROVEEDOR ---

        for i_prod_proveedor in range(num_productos_para_este_proveedor):
            if detener_creacion_total:  # Comprobar también dentro de este bucle
                break

            # Fecha mínima considerando el registro del proveedor
            fecha_min_por_proveedor = proveedor_actual.fecha_registro
            if i_prod_proveedor == 0:  # Solo para el primer producto de este proveedor
                fecha_min_por_proveedor += timedelta(
                    hours=random.randint(1, 12), minutes=random.randint(0, 59)
                )

            # Fecha mínima considerando la secuencia global (incremento variable)
            dias_inc = random.randint(0, 1)
            horas_inc = random.randint(
                0, 8
            )  # Reducido para permitir más productos en periodos cortos
            minutos_inc = random.randint(1, 59)  # Asegurar al menos 1 minuto
            segundos_inc = random.randint(0, 59)
            if dias_inc == 0 and horas_inc == 0 and minutos_inc == 0:
                minutos_inc = 1

            incremento_secuencial = timedelta(
                days=dias_inc,
                hours=horas_inc,
                minutes=minutos_inc,
                seconds=segundos_inc,
            )
            fecha_min_por_secuencia = (
                ultima_fecha_registro_global + incremento_secuencial
            )

            fecha_registro_propuesta = max(
                fecha_min_por_proveedor, fecha_min_por_secuencia
            )

            if fecha_registro_propuesta >= fecha_limite_absoluta_productos:
                incremento_secuencial_minimo = timedelta(
                    seconds=random.randint(1, 300)
                )  # 1 a 5 minutos
                fecha_min_por_secuencia_apretada = (
                    ultima_fecha_registro_global + incremento_secuencial_minimo
                )
                fecha_registro_apretada = max(
                    fecha_min_por_proveedor, fecha_min_por_secuencia_apretada
                )

                if fecha_registro_apretada >= fecha_limite_absoluta_productos:
                    logger.error(
                        f"No se puede generar fecha válida para producto {len(productos_creados) + 1} "
                        f"(proveedor {proveedor_actual.id}, producto {i_prod_proveedor + 1}/{num_productos_para_este_proveedor}). "
                        f"Fecha apretada ({fecha_registro_apretada}) supera límite ({fecha_limite_absoluta_productos}). "
                        f"Última fecha global: {ultima_fecha_registro_global}. Deteniendo creación."
                    )
                    detener_creacion_total = True
                    break
                else:
                    logger.warning(
                        f"Usando incremento de fecha apretado para producto {len(productos_creados) + 1} "
                        f"(proveedor {proveedor_actual.id}) para evitar límite de fecha."
                    )
                    fecha_registro = fecha_registro_apretada
            else:
                fecha_registro = fecha_registro_propuesta

            try:
                fecha_actualizacion = fecha_registro + timedelta(
                    minutes=random.randint(1, 30)
                )
                if (
                    fecha_actualizacion >= fecha_limite_absoluta_productos
                ):  # Asegurar que la actualización no pase el límite
                    fecha_actualizacion = fecha_limite_absoluta_productos - timedelta(
                        seconds=1
                    )
                if (
                    fecha_actualizacion <= fecha_registro
                ):  # Asegurar que la actualización sea posterior al registro
                    fecha_actualizacion = fecha_registro + timedelta(seconds=1)

                # Generar datos del producto
                categoria = random.choice(list(CategoriaProductoEnum))
                fragancia = random.choice(list(FraganciaProductoEnum))
                nombre_producto = ""
                descripcion_producto = ""

                # Generar nombre y descripción del producto
                try:
                    intentos_nombre = 0
                    max_intentos_nombre_ia = 5
                    nombre_base_generado_ia = ""

                    while intentos_nombre < max_intentos_nombre_ia:
                        nombre_propuesto = generar_nombre_producto_ia(
                            categoria.value, fragancia.value
                        )
                        if not nombre_base_generado_ia:
                            nombre_base_generado_ia = (
                                nombre_propuesto  # Guardar el primer nombre de IA
                            )

                        if (
                            nombre_propuesto
                            and nombre_propuesto not in nombres_productos_usados
                        ):
                            nombre_producto = nombre_propuesto
                            break
                        intentos_nombre += 1
                        logger.debug(
                            f"Nombre de producto IA duplicado o inválido ('{nombre_propuesto}'), "
                            f"reintentando ({intentos_nombre}/{max_intentos_nombre_ia})..."
                        )
                    else:  # Si el bucle while termina sin break
                        logger.warning(
                            f"No se pudo generar un nombre único con IA tras {max_intentos_nombre_ia} intentos "
                            f"para '{nombre_base_generado_ia}'. Usando fallback con sufijo."
                        )
                        sufijo_unico = 1
                        nombre_candidato = f"{nombre_base_generado_ia} ({sufijo_unico})"
                        while nombre_candidato in nombres_productos_usados:
                            sufijo_unico += 1
                            nombre_candidato = (
                                f"{nombre_base_generado_ia} ({sufijo_unico})"
                            )
                        nombre_producto = nombre_candidato

                    nombres_productos_usados.add(nombre_producto)
                    descripcion_producto = generar_descripcion_producto_ia(
                        nombre_producto, categoria.value, fragancia.value
                    )

                except Exception as e_ia:
                    logger.warning(
                        f"Error al generar texto con IA: {e_ia}. Usando alternativa de fallback."
                    )
                    nombre_base_fallback = (
                        f"{fake.word().capitalize()} de {fragancia.value}"
                    )
                    nombre_candidato_fallback = nombre_base_fallback
                    sufijo_unico = 1
                    while nombre_candidato_fallback in nombres_productos_usados:
                        nombre_candidato_fallback = (
                            f"{nombre_base_fallback} ({sufijo_unico})"
                        )
                        sufijo_unico += 1
                    nombre_producto = nombre_candidato_fallback
                    nombres_productos_usados.add(nombre_producto)
                    descripcion_producto = f"Vela aromática de {fragancia.value}. Ideal para ambientes acogedores."

                # Dimensiones de las velas realistas
                rangos = {
                    "Pequeña": {"alto": (5, 8), "ancho": (5, 8), "prof": (5, 8)},
                    "Mediana": {"alto": (9, 15), "ancho": (7, 8), "prof": (7, 8)},
                    "Grande": {"alto": (16, 25), "ancho": (10, 12), "prof": (10, 12)},
                }
                tamanio = random.choice(list(rangos.keys()))
                r = rangos[tamanio]
                alto = random.randint(*r["alto"])
                ancho = random.randint(*r["ancho"])
                prof = random.randint(*r["prof"])
                dimensiones = f"{alto}x{ancho}x{prof}cm"

                # Determinar el rango de peso según el tamaño
                if tamanio == "Pequeña":
                    peso = Decimal(str(round(random.uniform(0.150, 0.200), 3)))
                elif tamanio == "Mediana":
                    peso = Decimal(str(round(random.uniform(0.201, 0.270), 3)))
                else:  # Grande
                    peso = Decimal(str(round(random.uniform(0.271, 0.350), 3)))

                # URL de la imagen generada con IA
                try:
                    # Generar imagen utilizando Pollinations.ai
                    imagen_url = generate_image_pollinations(
                        categoria=categoria.value,
                        tamanio=tamanio,
                        fragancia=fragancia.value,
                        descripcion_producto=descripcion_producto,
                    )
                    # imagen_url = f"https://placekitten.com/300/{300 + len(productos_creados) % 100}"
                    if not imagen_url:
                        raise ValueError("URL de imagen vacía")
                except Exception as e:
                    logger.warning(
                        f"Error al generar imagen: {e}. Usando imagen de placeholder."
                    )
                    imagen_url = f"https://placekitten.com/300/{300 + len(productos_creados) % 100}"

                # Precios
                precio_proveedor = Decimal(
                    str(round(random.uniform(5000.00, 30000.00), -2))
                )  # Rango ajustado para COP, múltiplos de 100
                # Ajustar el incremento para que el precio de venta termine en 00 o 50
                incremento = round(random.uniform(5000.00, 20000.00), 0)
                incremento = incremento - (
                    incremento % 100
                )  # Redondear a múltiplo de 100
                if random.random() < 0.5:
                    incremento += 50  # 50% de probabilidad de terminar en 50
                precio_venta = precio_proveedor + Decimal(str(incremento))

                nuevo_producto = Producto(
                    nombre=nombre_producto,
                    descripcion=descripcion_producto,
                    precio_venta=precio_venta,
                    categoria=categoria,
                    peso=peso,
                    dimensiones=dimensiones,
                    imagen_url=imagen_url,
                    fragancia=fragancia,
                    periodo_garantia=90,  # 90 días
                    estado=EstadoProductoEnum.Activo,
                    precio_proveedor=precio_proveedor,
                    proveedor_id=proveedor_actual.id,
                    fecha_registro=fecha_registro,  # fecha_registro es la base para la creación
                    fecha_actualizacion=fecha_actualizacion,  # fecha_actualizacion es posterior
                )

                db.add(nuevo_producto)
                db.flush()

                productos_creados.append(nuevo_producto)
                ultima_fecha_registro_global = (
                    fecha_registro  # Actualizar para el siguiente producto global
                )
                productos_creados_proveedor_log[proveedor_actual.id] += 1

                # Commit cada 10 productos
                if len(productos_creados) % 10 == 0:
                    db.commit()

            except SQLAlchemyError as e:
                db.rollback()
                logger.error(
                    f"Error SQL al crear producto para proveedor {proveedor_actual.id}: {e}"
                )
            except Exception as e:  # pylint: disable=broad-except
                db.rollback()  # Rollback también para errores generales durante la creación de un producto
                logger.error(
                    f"Error inesperado al crear producto para proveedor {proveedor_actual.id}: {e}"
                )

        if (
            detener_creacion_total
        ):  # Si se detuvo en medio de los productos de un proveedor
            logger.info(
                f"Proveedor {proveedor_actual.id}: "
                f"{productos_creados_proveedor_log[proveedor_actual.id]}/{num_productos_para_este_proveedor} "
                f"productos creados antes de la detención."
            )
        else:
            logger.info(
                f"Proveedor {proveedor_actual.id}: "
                f"{productos_creados_proveedor_log[proveedor_actual.id]}/{num_productos_para_este_proveedor} "
                f"productos creados."
            )

    if productos_creados:
        try:
            db.commit()
            logger.info(
                f"Se han creado {len(productos_creados)}/{count} productos en total."
            )
            # Log de distribución final por proveedor
            # (El log por proveedor ya se hizo dentro del bucle)
        except Exception as e:  # pylint: disable=broad-except
            db.rollback()
            logger.error(f"Error al hacer commit final de productos: {e}")

    return productos_creados


def get_productos(db: Session) -> list[Any] | list[type[Producto]]:
    """
    Obtiene todos los productos activos de la base de datos.

    Args:
        db: Sesión de base de datos

    Returns:
        Lista de productos activos
    """
    try:
        productos = db.query(Producto).all()
        logger.info(f"Total de productos obtenidos: {len(productos)}")
        return productos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener productos: {e}")
        return []
