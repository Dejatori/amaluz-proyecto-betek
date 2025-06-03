import re
import unicodedata


def sanear_string_para_correo(texto: str) -> str:
    """
    Sanea una cadena de texto para ser utilizada como parte de un correo electrónico.
    Convierte a minúsculas, elimina tildes, reemplaza espacios con guiones bajos
    y elimina caracteres no alfanuméricos excepto el guion bajo.
    """
    # Normalizar para descomponer tildes y caracteres especiales
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    # Codificar a ASCII ignorando caracteres no ASCII (elimina tildes)
    texto_ascii = texto_normalizado.encode("ascii", "ignore").decode("ascii")
    # Convertir a minúsculas
    texto_minusculas = texto_ascii.lower()
    # Reemplazar espacios y múltiples guiones bajos con un solo guion bajo
    texto_con_guiones = re.sub(r"\s+", "_", texto_minusculas)
    # Eliminar caracteres no alfanuméricos excepto el guion bajo
    texto_saneado = re.sub(r"[^\w_]", "", texto_con_guiones)
    # Asegurar que no haya múltiples guiones bajos seguidos
    texto_saneado = re.sub(r"_+", "_", texto_saneado)
    return texto_saneado
