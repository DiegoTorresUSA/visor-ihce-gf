import requests
import time
from .config import settings

CODIGOS_TRANSITORIOS = {500, 502, 503, 504}

class FHIRHttpClient:

    def __init__(self, timeout: int =30, max_retries: int = 3, backoff_base: float = 0.5):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base


    def _es_transitorio(self, response: requests.Response):
        """
        Esta respuesta es un fallo pasajero del servidor?
        """
        return response.status_code in CODIGOS_TRANSITORIOS


    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": settings.APIM_SUBSKEY,
            "x-functions-key": settings.API_KEY
        }

    def _request(self, metodo: str, token: str, path: str,
                 json_body: dict | None = None,
                 params: dict | None = None) -> requests.Response:
        url = f"{settings.APIM_URL}{path}"
        headers = self._headers(token)
        ultima = None

        for intento in range(1, self.max_retries + 1):
            try:
                response = requests.request(metodo, url, headers=headers, json=json_body, params=params, timeout=self.timeout)
                if not self._es_transitorio(response):
                    return response
                ultima = response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                ultima = None

            if intento < self.max_retries:
                time.sleep(self.backoff_base * (2 ** (intento - 1)))

        if ultima is not None:
            return ultima
        raise requests.exceptions.RequestException(
            f"falló {metodo} {url} tras {self.max_retries} intentos (errores de red)."
        )


    def get(self, token: str, path: str) -> requests.Response:
        return self._request("GET", token, path)

    def post(self, token: str, path: str, json_body: dict | None = None, params: dict | None = None) -> requests.Response:
        return self._request("POST", token, path, json_body=json_body, params=params)

    def put(self, token: str, path: str) -> requests.Response:
        return self._request("PUT", token, path)

fhir = FHIRHttpClient()