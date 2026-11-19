import json
from app.core.config import settings
from app.core.token_manager import obtener_token_valido
from app.core.http_client import fhir
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


class PacienteService:
    def __init__(self, cliente, token=obtener_token_valido):
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


    def buscar_similar(self, tipo_documento: str, numero_documento: str, usuario_humano: str) -> list[PacienteVista]:
        #Parada 1 - Armo el sobre
        consulta = ConsultaPacienteSimilar(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            usuario_humano=usuario_humano
        )
        body = consulta.crear_json_fhir()
        #Parada 2 - Pedirle la carpeta al mensajero
        payload = self._consultar(settings.IHCE_CONSULTAR_PACIENTE_SIMILAR, body)
        # Parada 3 - Abrir la carpeta
        pacientes = _extraer_pacientes(payload)
        # Parada 4 - Busqueda de pacientes
        if not pacientes:
            raise PacienteNoEncontrado("la consulta no devolvió pacientes para los datos enviados")
        #Parada 5 — traducir y devolver
        vistas = []
        for patient in pacientes:
            vistas.append(mapear_paciente(patient))
        return vistas


    def buscar_exacto(self, tipo_documento: str, numero_documento: str, usuario_humano: str) -> PacienteVista:
        # Parada 1 - Armo el sobre
        consulta_exacto = ConsultaPacienteExacto(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            usuario_humano=usuario_humano
        )
        body = consulta_exacto.crear_json_fhir()
        #Parada 2 - Pedirle la carpeta al mensajero
        payload = self._consultar(settings.IHCE_CONSULTAR_PACIENTE_EXACTO, body)
        # Parada 3 - Abrir la carpeta
        pacientes = _extraer_pacientes(payload)
        # Parada 4 - Busqueda de pacientes
        if not pacientes:
            raise PacienteNoEncontrado("la consulta no devolvió pacientes para los datos enviados")
        return mapear_paciente(pacientes[0])

servicio = PacienteService(fhir)