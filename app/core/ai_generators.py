"""
Módulo para funciones de generación de contenido utilizando IA.
Contiene funciones que interactúan con modelos de IA para generar nombres, descripciones e imágenes.
"""
import logging
import urllib.parse

import httpx

from pydantic_ai import Agent, format_as_xml
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import config
from app.core.tasks import APIResponseError

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del agente de AI
ollama_model = OpenAIModel(
    "llama3.2", provider=OpenAIProvider(base_url=config.OLLAMA_API_URL)
)
agent = Agent(
    ollama_model,
    system_prompt="La respuesta debe estar perfectamente escrita en español, sin errores ortográficos ni gramaticales, sin comillas ni puntuación adicional."
)

def determinar_genero_persona(nombre: str) -> str:
    """
    Determina el género de una persona basándose en su nombre.
    Intenta extraer 'Masculino', 'Femenino' u 'Otro' incluso si la IA
    devuelve texto adicional.

    Args:
        nombre: Nombre de la persona

    Returns:
        Género de la persona ('Masculino', 'Femenino' o 'Otro')
    """
    prompt = (
        f"""\
        Rol: Actúa como un experto en determinación de género basado en nombres, con excelente dominio del español.
        Tarea: Determina el género de una persona basándote únicamente en su nombre.
        Contexto: El nombre proporcionado es '{nombre}'. El género debe ser uno de los siguientes: 'Masculino' o 'Femenino'.
        Formato de retorno: Devuelve únicamente el género como una cadena de texto simple. No incluyas comillas ni puntuación adicional al final.
        Advertencias: La respuesta debe estar perfectamente escrita en español, sin errores ortográficos ni gramaticales.
        """
    )
    result = agent.run_sync(prompt)
    raw_output = result.output.strip()
    output_lower = raw_output.lower()

    # Paso 1: Buscar palabras clave de género en el texto completo (insensible a mayúsculas/minúsculas).
    genre_from_text_search = None
    if any(word in output_lower for word in ["masculino", "masculina", "hombre", "hombres", "varón"]):
        genre_from_text_search = "Masculino"
    elif any(word in output_lower for word in ["femenino", "femenina", "mujer", "mujeres"]):  # Usar elif para dar precedencia
        genre_from_text_search = "Femenino"

    # Paso 2: Verificar si la salida (después de quitar un posible punto final)
    # es exactamente una de las opciones válidas.
    # Esto tiene prioridad si la IA responde correctamente con solo la palabra clave.
    final_genre = None
    cleaned_output_for_exact_match = raw_output
    if cleaned_output_for_exact_match.endswith("."):
        cleaned_output_for_exact_match = cleaned_output_for_exact_match[:-1].strip()

    if cleaned_output_for_exact_match in ['Masculino', 'Femenino']:
        final_genre = cleaned_output_for_exact_match
    elif genre_from_text_search:
        # Si la coincidencia exacta falló, pero la búsqueda en texto encontró algo.
        final_genre = genre_from_text_search
    else:
        final_genre = 'Otro'

    return final_genre

def generar_nombre_producto_ia(categoria: str, fragancia: str) -> str:
    """
    Genera un nombre para un producto de vela usando IA.

    Args:
        categoria: Categoría del producto
        fragancia: Fragancia del producto

    Returns:
        Nombre generado para el producto
    """
    prompt = (
        "Rol: Actúa como un creativo de marketing especializado en la creación de nombres de productos para el hogar.\n"
        "Tarea: Genera un nombre único, atractivo y memorable para una vela.\n"
        f"Contexto: La vela pertenece a la categoría '{categoria}' y tiene una fragancia de '{fragancia}'. El nombre debe ser corto y evocador.\n"
        "Formato de retorno: Devuelve únicamente el nombre del producto como una cadena de texto simple. No incluyas comillas ni ninguna puntuación al final del nombre.\n"
        "Advertencias: Evita nombres genéricos o demasiado largos. El nombre debe ser original y fácil de recordar."
    )
    result = agent.run_sync(prompt)
    nombre = result.output.strip()
    # Eliminar punto final si existe
    if nombre.endswith("."):
        nombre = nombre[:-1].strip()
    return nombre


def generar_descripcion_producto_ia(nombre: str, categoria: str, fragancia: str) -> str:
    """
    Genera una descripción para un producto de vela usando IA.

    Args:
        nombre: Nombre del producto
        categoria: Categoría del producto
        fragancia: Fragancia del producto

    Returns:
        Descripción generada para el producto
    """
    prompt = (
        "Rol: Actúa como un redactor publicitario experto en descripciones de productos de bienestar y hogar, con excelente dominio del español.\n"
        f"Tarea: Crea una descripción breve (1-3 frases), evocadora y gramaticalmente impecable para la vela llamada '{nombre}'.\n"
        f"Contexto: Esta vela es de la categoría '{categoria}' y su fragancia es '{fragancia}'. La descripción debe resaltar la experiencia sensorial y el ambiente que la vela ayuda a crear.\n"
        "Formato de retorno: Devuelve únicamente la descripción del producto como una cadena de texto simple. No incluyas comillas alrededor de la descripción.\n"
        "Advertencias: Enfócate en las sensaciones y el ambiente. No menciones materiales de fabricación. Evita afirmaciones exageradas. La descripción debe ser concisa, atractiva y estar perfectamente escrita en español, sin errores ortográficos ni gramaticales."
    )
    result = agent.run_sync(prompt)
    descripcion = result.output.strip()
    return descripcion


def generate_image_pollinations(categoria: str, tamanio: str, fragancia: str, descripcion_producto: str) -> str:
    """
    Genera una imagen utilizando Pollinations.ai y devuelve una URL acortada.

    Args:
        categoria: Categoría del producto
        tamanio: Tamaño del producto
        fragancia: Fragancia del producto
        descripcion_producto: Descripción del producto para guiar la generación de la imagen

    Returns:
        URL acortada que redirecciona a la imagen

    Raises:
        APIResponseError: Si hay un error en la solicitud a la API
    """
    try:
        image_prompt = (
            f"Fotografía de producto profesional y elegante de una vela detallada, sin ningún texto, etiqueta o marca de agua visible en la imagen. "
            f"Categoría: '{categoria}', Tamaño: '{tamanio}', Fragancia principal: '{fragancia}'. "
            f"La vela debe tener un diseño elegante y moderno, con una forma distintiva que la haga destacar. "
            f"La llama debe ser visible, iluminando suavemente la cera. "
            f"Fondo: blanco puro, minimalista y limpio, con sombras suaves y naturales proyectadas por la vela para dar profundidad. "
            f"Iluminación: tipo estudio profesional, principalmente lateral suave, diseñada para resaltar la textura de la cera y la forma tridimensional de la vela. "
            f"Tonalidad general de la imagen y ambiente: deben evocar sutilmente la esencia y las sensaciones asociadas a la fragancia '{fragancia}'. "
            f"Estilo visual general: limpio, moderno, sofisticado, y de alta calidad comercial. "
            f"Importante: La imagen final no debe contener ningún tipo de texto superpuesto, etiquetas, logotipos o marcas de agua. Solo la vela y el fondo descrito. "
            f"Inspiración contextual del producto (para guiar el ambiente y la sutileza de la representación): \"{descripcion_producto}\""
        )

        encoded_image_prompt = urllib.parse.quote(image_prompt)

        pollinations_params = "?width=1024&height=1024&seed=42&model=flux"
        pollinations_url = f"https://pollinations.ai/p/{encoded_image_prompt}{pollinations_params}"

        # Acortar la URL con TinyURL
        acortar_url_endpoint = "https://tinyurl.com/api-create.php"
        response = httpx.get(
            acortar_url_endpoint, params={"url": pollinations_url}, timeout=20.0
        )
        response.raise_for_status()

        url_acortada = response.text

        return url_acortada

    except httpx.HTTPStatusError as err:
        logger.error(f"Solicitud a Pollinations fallida: {err}")
        raise APIResponseError(
            f"La solicitud ha fallado con código de estado: {err.response.status_code}"
        ) from err
    except httpx.RequestError as err:
        logger.error(f"Error de conexión a Pollinations: {err}")
        raise APIResponseError(f"Error de conexión: {str(err)}") from err


def generate_descripcion_localizacion_ia() -> str:
    """
    Genera una descripción para una localización de entrega usando IA.

    Returns:
        Descripción generada para la localización
    """
    prompt = (
        "Rol: Actúa como un asistente de logística redactando información complementaria para direcciones de entrega en español.\n"
        "Tarea: Genera una descripción breve, útil y gramaticalmente correcta de una localización para facilitar su identificación por un repartidor.\n"
        "Contexto: La descripción complementará una dirección formal. Debe incluir detalles visuales distintivos del lugar (ej: color de la fachada, tipo de puerta, algún punto de referencia cercano visible desde la calle). El objetivo es ayudar al repartidor a encontrar el punto de entrega exacto rápidamente.\n"
        "Formato de retorno: Devuelve únicamente la descripción de la localización como una cadena de texto simple (ej: 'Casa esquina de dos pisos, color amarillo con rejas negras'). No incluyas comillas ni puntuación innecesaria al final.\n"
        "Advertencias: La descripción debe ser objetiva, concisa, enfocada en características físicas observables desde el exterior y estar perfectamente escrita en español, sin errores ortográficos ni gramaticales. Evita información personal, subjetiva o instrucciones complejas."
    )
    result = agent.run_sync(prompt)
    descripcion = result.output.strip()
    # Eliminar punto final si existe
    if descripcion.endswith("."):
        descripcion = descripcion[:-1].strip()
    return descripcion


def generate_notas_entrega_ia() -> str:
    """
    Genera notas de entrega para un pedido usando IA.

    Returns:
        Notas de entrega generadas
    """
    prompt = (
        "Rol: Actúa como un cliente especificando instrucciones claras para la entrega de un paquete, en español.\n"
        "Tarea: Genera notas de entrega breves, precisas y gramaticalmente correctas para un pedido.\n"
        "Contexto: Estas notas son para el repartidor y deben indicar preferencias o instrucciones importantes para la entrega (ej: 'Dejar en portería con Juan Pérez', 'Timbre no funciona, llamar al llegar', 'Entregar solo por la tarde después de las 2 PM').\n"
        "Formato de retorno: Devuelve únicamente las notas de entrega como una cadena de texto simple. No incluyas comillas ni puntuación innecesaria al final.\n"
        "Advertencias: Las notas deben ser directas, accionables, lo más concisas posible y estar perfectamente escritas en español, sin errores ortográficos ni gramaticales. Evita información sensible o ambigua."
    )
    result = agent.run_sync(prompt)
    nota = result.output.strip()
    return nota


def generate_comentario_ia(context: str) -> str:
    """
    Genera un comentario para un producto usando IA.

    Args:
        context: Contexto para la generación del comentario

    Returns:
        Comentario generado
    """
    prompt = (
        "Rol: Actúa como un cliente que ha comprado y usado un producto y ahora está escribiendo una reseña online, en español.\n"
        "Tarea: Escribe un comentario breve (1-3 frases), auténtico y gramaticalmente impecable sobre un producto, basándote en la información y la calificación proporcionada en el contexto.\n"
        f"Contexto: La reseña es para el siguiente producto y calificación: '{context}'. El comentario debe reflejar la experiencia de un cliente real.\n"
        "Formato de retorno: Devuelve únicamente el texto del comentario como una cadena de texto simple. No incluyas comillas alrededor del comentario.\n"
        "Advertencias: El tono del comentario debe ser realista y coherente con la calificación indicada. Si la calificación es baja, el comentario debe expresar insatisfacción de manera creíble (pero preferiblemente constructiva). Si es alta, debe expresar satisfacción. Evita lenguaje genérico. El comentario debe estar perfectamente escrito en español, sin errores ortográficos ni gramaticales."
    )
    result = agent.run_sync(prompt)
    comentario = result.output.strip()
    return comentario