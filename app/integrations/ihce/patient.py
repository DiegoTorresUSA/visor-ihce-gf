import requests
from app.core.http_client import fhir
from app.core.config import settings

def consultar_paciente_similar(token:str, json_fhir:dict) -> requests.Response:
    """
    Llama a la operación $consultar-paciente-similar del mecanismo IHCE.

    Args:
        token: Token Bearer válido obtenido desde Azure AD
        json_fhir: Estructura Parameters de FHIR con los datos de búsqueda

    Returns:
        Respuesta HTTP del APIM/IHCE
    """
    return fhir.post(
        token,
        settings.IHCE_CONSULTAR_PACIENTE_SIMILAR,
        json_body=json_fhir
    )

def consultar_paciente_exacto(token:str, json_fhir:dict) -> requests.Response:
    """
        Llama a la operación $consultar-paciente-exacto del mecanismo IHCE.

        Args:
            token: Token Bearer válido obtenido desde Azure AD
            json_fhir: Estructura Parameters de FHIR con los datos de búsqueda

        Returns:
            Respuesta HTTP del APIM/IHCE
        """
    return fhir.post(
        token,
        settings.IHCE_CONSULTAR_PACIENTE_EXACTO,
        json_body=json_fhir
    )