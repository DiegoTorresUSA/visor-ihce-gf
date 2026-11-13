import json

from requests import RequestException
from app.core.token_manager import obtener_token_valido
from app.integrations.ihce.patient import consultar_paciente_exacto, consultar_paciente_similar
from app.integrations.ihce.paciente_mapper import mapear_paciente
from app.schemas.request.paciente_request import ConsultaPacienteExacto, ConsultaPacienteSimilar
from app.schemas.view.paciente_view import PacienteVista
import requests

class ErrorConsultaIHCE(Exception):
    """Falla al comunicarse con el mecanismo IHCE."""

class PacienteNoEncontrado(Exception):
    """La consulta se completó correctamente pero no devolvió pacientes."""


def _extraer_pacientes(payload: dict) -> list[dict]:
    """
        Devuelve la lista de recursos Patient contenidos en la respuesta.
        Acepta un Bundle (searchset) o un Patient suelto.
    """
    tipo = payload.get('resourceType')

    if tipo == 'Patient':
        return [payload]

    if tipo != "Bundle":
        raise ErrorConsultaIHCE(f"respuesta inesperada del mecanismo IHCE: {tipo}")

    return [
        entry["resource"]
        for entry in payload.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == "Patient"
            ]


def buscar_paciente_similar(tipo_documento: str, numero_documento: str, human_user: str) -> list[PacienteVista]:
    """
        Consulta $consultar-paciente-similar y devuelve los pacientes encontrados.
        Lanza ErrorConsultaIHCE si no se pudo consultar.
    """
    #construyo la peticion
    #convertirlo a parameters
    #obtengo el token
    #llamar al mecanismo
    #valido el status
    #capturo los datos convertidos a JSON
    #proceso lo que nececesito
    #los mapeo
    #devuelvo el paciente

    p = ConsultaPacienteSimilar(tipo_documento, numero_documento, human_user)
    body = p.crear_json_fhir()


class PacienteService:
    def __init__(self, cliente, token):
        self._cliente = cliente
        self._token = token

    def _consultar(self, path, body) -> dict:

        token = self._token()
        try:
            response = self._cliente.post(token, path, json_body=body)
        except requests.exceptions.RequestException as e:
            raise ErrorConsultaIHCE(f"falló la consulta a {path}: {e}") from e

        if not (200 <= response.status_code <= 299):
            raise ErrorConsultaIHCE(f"{response.status_code} en {path}: {response.text[:300]}")

        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            raise ErrorConsultaIHCE(f"respuesta no es un JSON de {path}: {e}") from e