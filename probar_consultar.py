import requests
import json

from app.services.paciente_service import PacienteService, ErrorConsultaIHCE, PacienteNoEncontrado

PATH = "/rda/Patient/$consultar-paciente-similar"
BODY = {"resourceType": "Parameters", "parameter": []}

BUNDLE_CON_UN_PACIENTE = {
    "resourceType": "Bundle",
    "total": 1,
    "entry": [
        {"resource": {
            "resourceType": "Patient",
            "id": "pac-1",
            "identifier": [{
                "use": "official",
                "type": {"coding": [{
                    "system": "https://fhir.minsalud.gov.co/rda/CodeSystem/ColombianPersonIdentifier",
                    "code": "CC",
                }]},
                "value": "12345678",
            }],
            "name": [{
                "use": "official",
                "family": "Pérez",
                "given": ["Juan"],
            }],
        }},
    ],
}

def fabricar_response(status: int, cuerpo:str) -> requests.Response:
    """Crea un Response real de requests, pero sin pasar por la red."""
    r = requests.Response()
    r.status_code = status
    r.encoding = "utf-8"
    r._content = cuerpo.encode("utf-8")
    return r


class ClienteFalso:
    """Implementa solo lo que el servicio usa: post."""

    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.paths = []

    def post(self, token:str, path:str, json_body=None, params=None):
        self.paths.append(path)
        if self._error is not None:
            raise self._error
        return self._response

def token_falso() -> str:
    return "token de prueba"


def ejecutar(nombre:str, cliente:ClienteFalso) -> None:
    servicio = PacienteService(cliente, token_falso)

    try:
        resultado = servicio._consultar(PATH, BODY)
        print(f"[{nombre}] OK -> {resultado}")
    except ErrorConsultaIHCE as e:
        print(f"[{nombre}] ErrorConsultaIHCE -> {e}")

def probar_buscar_similar():
    print("prueba de similar--------")
    cliente = ClienteFalso(response=fabricar_response(
        200, '{"resourceType": "Bundle", "total": 0, "entry": []}'))
    servicio = PacienteService(cliente, token_falso)
    try:
        servicio.buscar_similar("CC", "12345678", "juan@correo.com")
        print("[parada 4] NO LANZÓ (mal)")
    except PacienteNoEncontrado as e:
        print("[parada 4] PacienteNoEncontrado OK ->", e)
    print("fin de similar--------")

def probar_resultados():
    print("prueba de general--------")
    cliente = ClienteFalso(response=fabricar_response(
        200, json.dumps(BUNDLE_CON_UN_PACIENTE)))
    servicio = PacienteService(cliente, token_falso)
    vistas = servicio.buscar_similar("CC", "12345678", "juan@correo.com")
    print("[parada 5] cantidad:", len(vistas))
    for vista in vistas:
        print("   ", vista.nombre_completo, "|", vista.tipo_documento, vista.numero_documento)
    print("fin de general--------")

def probar_resultados_exacto():
    print("prueba de exacto--------")
    cliente = ClienteFalso(response=fabricar_response(
        200, json.dumps(BUNDLE_CON_UN_PACIENTE["entry"][0]["resource"])))
    servicio = PacienteService(cliente, token_falso)
    vista = servicio.buscar_exacto("CC", "12345678", "juan@correo.com")
    print("   ", vista.nombre_completo, "|", vista.tipo_documento, vista.numero_documento)
    print("    path usado:", cliente.paths[-1])
    print("fin de exacto--------")


if __name__ == "__main__":
    probar_buscar_similar()
    probar_resultados()
    probar_resultados_exacto()
    ejecutar(
        "1. 200 + Bundle",
        ClienteFalso(response=fabricar_response(
            200, '{"resourceType": "Bundle", "total": 0, "entry": []}')),
    )
    ejecutar(
        "2. 502",
        ClienteFalso(response=fabricar_response(
            502, '{"message": "bad gateway"}')),
    )
    ejecutar(
        "3. 200 + HTML",
        ClienteFalso(response=fabricar_response(
            200, "<html>error del proxy</html>")),
    )
    ejecutar(
        "4. timeout",
        ClienteFalso(error=requests.exceptions.Timeout("timeout simulado")),
    )
    ejecutar(
        "5. 300 (borde)",
        ClienteFalso(response=fabricar_response(
            300, '{"message": "multiple choices"}')),
    )

