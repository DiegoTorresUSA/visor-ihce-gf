import time
from .auth_client import get_access_token

_token = None
_expira_en = 0.0

def obtener_token_valido(forzar: bool = False) -> str:
    global _expira_en, _token
    ahora = time.time()
    if forzar or _token is None or ahora >= _expira_en:
        token, respuesta = get_access_token()
        if token is None:
            raise RuntimeError('No se pudo obtener token de acceso')
        expires_in = respuesta.json().get('expires_in', 3599) # 3599 = valor real del tenant; fallback por si falta
        _token = token
        _expira_en = ahora + expires_in -60
    return _token
