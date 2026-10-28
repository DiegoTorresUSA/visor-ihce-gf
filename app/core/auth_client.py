import requests
from .config import settings

def get_access_token(secret_override:str | None = None) -> tuple[str | None, requests.Response] :
    """
    Realizamos la solicitud del token. 
    Si secret_override tiene algo, lo usaremos en lugar del secreto real.
    """

    secret_to_use = secret_override if secret_override else settings.CLIENT_SECRET

    # 1. Los datos que el servidor espera (el 'Body' en Postman)
    payload = {
        'grant_type': 'client_credentials',
        'client_id': settings.CLIENT_ID,
        'client_secret': secret_to_use, # <--- Usamos la variable elegida
        'scope': settings.SCOPE
    }

    try:
        response = requests.post(settings.AUTH_URL, data=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"No se pudo contactar el servidor de identidad: {e}") from e

    token_data = response.json().get('access_token') if response.status_code == 200 else None
    return token_data, response