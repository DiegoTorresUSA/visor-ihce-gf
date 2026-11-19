# ESTADO DEL PROYECTO - Visor IHCE + Gestión Farmacéutica Colombia

## Última actualización
Fecha: 2026-11-18
Commit de referencia: `32711db` (docs: update status after buscar_similar)
Cambios locales sin commitear al cierre de esta sesion: `app/services/paciente_service.py` (metodo `buscar_exacto`, default del proveedor de token y singleton `servicio`) y `probar_consultar.py` (prueba de `buscar_exacto` y registro de `paths` en el cliente falso)

## Resumen de un vistazo

| Incremento | Estado |
| :-- | :-- |
| 0.1 Infraestructura base (config, auth, HTTP, /health) | CERRADO |
| 0.2 Cliente IHCE + contrato de vista de paciente | CERRADO |
| 0.3 Mapper `Patient -> PacienteVista` | CERRADO |
| 0.4 Servicio de pacientes (3 de 3 metodos, validados) | CERRADO (pendiente de commit) |
| 0.5 API + UI (router y plantillas) | SIGUIENTE |

Ultima accion realizada: `buscar_exacto` implementado y validado con cliente falso (un `Patient` suelto -> una `PacienteVista`; el path registrado es `/Patient/$consultar-paciente-exacto`). Ademas, `__init__` ya tiene `token=obtener_token_valido` por defecto y existe la instancia unica `servicio = PacienteService(fhir)`.

Proximo paso: commit de cierre de 0.4 y arranque de 0.5 (router `app/api/routers/pacientes.py`, `home.py`, plantillas y registro en `main.py`). La prueba real contra el APIM con datos ficticios queda como verificacion opcional antes del commit.

---

## QUE ESTA HECHO

### 0.1 - Infraestructura base (CERRADO)

- [x] Estructura de carpetas creada (`app/core`, `app/integrations`, `app/schemas`, `app/services`, `app/api`, `app/templates`, `app/static`)
- [x] `.venv` creado e interprete configurado
- [x] `requirements.txt` con dependencias minimas (`requests==2.31.0`, FastAPI, Uvicorn, Pydantic v2, pydantic-settings)
- [x] `app/core/config.py` (pydantic-settings leyendo `.env`)
- [x] `app/core/auth_client.py` (OAuth2 client_credentials)
- [x] `app/core/http_client.py` (`FHIRHttpClient`: headers APIM, reintentos, backoff)
- [x] `app/core/token_manager.py` (cache de token con renovacion anticipada)
- [x] Imports relativos corregidos a `app.core.*`
- [x] `.env` copiado desde `AutomatedUatIHCE` (local, no versionado)
- [x] `.gitignore` y `.env.example` creados
- [x] Git inicializado y repositorio publicado en `github.com/DiegoTorresUSA/visor-ihce-gf`
- [x] `README.md` creado, con auditoria de secretos (`.env` nunca commiteado)
- [x] `app/main.py` con `GET /health`
- [x] Validado con uvicorn: `/health` y `/docs` responden

### 0.2 - Cliente IHCE y contrato de vista (CERRADO)

Codigo:

- [x] `app/integrations/ihce/patient.py` con `consultar_paciente_similar()` y `consultar_paciente_exacto()`, usando `fhir.post(token, path, json_body=...)`
  - Nota: desde 0.4 estas funciones quedaron **sin uso**; el servicio arma el body y llama `_consultar`. No borrar todavia: primero hay que quitar el import muerto del servicio
- [x] `app/schemas/request/paciente_request.py` con `ConsultaPacienteSimilar` y `ConsultaPacienteExacto` (ambos con `usuario_humano` y `crear_json_fhir()`)
- [x] `app/schemas/view/paciente_view.py` con `PacienteVista` (9 campos `Optional[str]`)

Validaciones realizadas:

- [x] `obtener_token_valido()` devuelve un token `str` valido contra el tenant
- [x] `crear_json_fhir()` genera un `Parameters` identico al body de Postman (`identifier.part` + `humanuser`)
- [x] La llamada real a `$consultar-paciente-similar` devuelve un `Bundle` con recursos `Patient`
- [x] `$consultar-paciente-exacto` devuelve un `Patient` suelto, no un `Bundle`

Hallazgos de estructura real del `Patient`:

- [x] `name[]`: `use` (`official`), `family` concatenado, `_family.extension[]` con `ExtensionFathersFamilyName` y `ExtensionMothersFamilyName`, `given[]` ordenado
- [x] `identifier[]`: `use` (`official`), `type.coding[]` con dos codings (`v2-0203/PN` generico y `ColombianPersonIdentifier/CC`), `system` RNEC y `value`

### 0.3 - Mapper `Patient -> PacienteVista` (CERRADO)

Codigo:

- [x] `PacienteVista` ampliado con `@property nombre_completo` (concatenacion filtrada, no entra en `model_dump()`)
- [x] `app/integrations/ihce/paciente_mapper.py` creado con las constantes del dominio:
  - `URL_APELLIDO_PATERNO`
  - `URL_APELLIDO_MATERNO`
  - `SISTEMA_TIPO_DOCUMENTO`
- [x] Helpers privados:
  - `_elegir_nombre(nombres)` -> HumanName oficial, fallback al primero, `{}` si vacio
  - `_valor_extension(extensiones, url)` -> `valueString` o `None`
  - `_apellidos(nombre)` -> `(primer_apellido, segundo_apellido)` con fallback a `family` sin partir
  - `_nombres(nombre)` -> `(primer_nombre, segundo_nombre)` desde `given[]`
  - `_documento(identifiers)` -> `(tipo, numero)`; prefiere `use=official` y exige el CodeSystem colombiano
- [x] Funcion publica `mapear_paciente(patient) -> PacienteVista`
- [x] Sin rastros de depuracion (`print` eliminado) y estilo de firmas corregido

Validaciones realizadas (datos ficticios, sin red):

- [x] `nombre_completo`: completo, parcial y modelo vacio (sin doble espacio, sin `TypeError`)
- [x] `_apellidos`: extensiones, solo `family`, y diccionario vacio
- [x] `_nombres`: dos nombres, uno, ninguno, y tres (el resto se une en el segundo)
- [x] `_documento`: pasaporte antes que CC oficial, lista vacia, identificador sin `type`
- [x] `mapear_paciente`: paciente completo mapea los 9 campos; `{}` devuelve todos en `None`

Errores de aprendizaje documentados:

- [x] `return` mal indentado dentro del `for` cortaba la busqueda en la primera vuelta
- [x] El REPL conserva modulos en `sys.modules`: hay que reiniciar el interprete o usar `importlib.reload`
- [x] Diferencia entre `Response` crudo, `Bundle` y `Patient`: el mapper solo recibe el `Patient`

### 0.4 - Servicio de pacientes (CERRADO)

El servicio es una **clase** (`PacienteService`), no funciones sueltas, porque tiene dependencias inyectables: el cliente HTTP y el proveedor de token.

Codigo construido:

- [x] `ErrorConsultaIHCE` -> falla de transporte o de formato al hablar con el mecanismo
- [x] `PacienteNoEncontrado` -> la consulta se completo pero no devolvio pacientes
- [x] `_extraer_pacientes(payload)` -> acepta un `Bundle` y tambien un `Patient` suelto; cualquier otro `resourceType` es `ErrorConsultaIHCE`
- [x] `PacienteService.__init__(self, cliente, token=obtener_token_valido)` -> guarda `self._cliente` y `self._token` (la funcion, no el token). Sin parentesis: el token se pide cuando se usa, no al importar
- [x] `PacienteService._consultar(self, path, body) -> dict` -> token + `post` + status 2xx + JSON, con dos `try` angostos

Validacion de `_consultar` (CERRADA):

Script `probar_consultar.py` en la raiz (versionado en `60b1393`). Usa un `ClienteFalso` con metodo `post`, un `token_falso()` y `requests.Response` reales fabricados sin red. Resultado: 5 de 5.

- [x] 200 + `Bundle` vacio -> devuelve el `dict`
- [x] 502 -> `ErrorConsultaIHCE` con status + path + cuerpo recortado
- [x] 200 + cuerpo no JSON (HTML) -> `ErrorConsultaIHCE`
- [x] timeout de red -> `ErrorConsultaIHCE` **sin tocar `response`** (delata el `UnboundLocalError` de la version rota)
- [x] 300 -> `ErrorConsultaIHCE` (borde de la familia 2xx)

Nota: en la consola de PowerShell la tilde de `fallo` sale mal renderizada. Es la codepage, no el codigo.

Implementacion de `buscar_similar` (CERRADA):

Cinco paradas, cada una con una unica responsabilidad:

- [x] Parada 1: armar el `Parameters` con `ConsultaPacienteSimilar(...)` + `crear_json_fhir()` (argumentos con nombre: Pydantic v2 no acepta posicionales)
- [x] Parada 2: `self._consultar(settings.IHCE_CONSULTAR_PACIENTE_SIMILAR, body)` -> devuelve el `payload`
- [x] Parada 3: `_extraer_pacientes(payload)` -> lista de `Patient`
- [x] Parada 4: si la lista viene vacia -> `PacienteNoEncontrado` (mensaje sin numero de documento)
- [x] Parada 5: `for` + `append` con `mapear_paciente()` y `return vistas`
- [x] Decision: el `path` sale de `settings` dentro del servicio; la URL base la arma `http_client`
- [x] Decision: mapeo con `for` + `append` por claridad didactica
- [x] Borrada la funcion antigua `buscar_paciente_similar()`, que tenia un bug latente (Pydantic v2 no acepta argumentos posicionales y nunca se ejecuto)

Validacion de `buscar_similar` (CERRADA):

- [x] `Bundle` vacio (`entry: []`) -> `PacienteNoEncontrado`
- [x] `Bundle` con un `Patient` -> 1 `PacienteVista` con `nombre_completo` "Juan Perez" y documento `CC 12345678`
- [x] Los 5 casos de `_consultar` siguen pasando despues del cambio

Implementacion de `buscar_exacto` (CERRADA):

- [x] Parada 1: `ConsultaPacienteExacto(...)` + `crear_json_fhir()`
- [x] Parada 2: `self._consultar(settings.IHCE_CONSULTAR_PACIENTE_EXACTO, body)`
- [x] Parada 3: `_extraer_pacientes(payload)` -> lista de `Patient` (acepta el `Patient` suelto)
- [x] Parada 4: si la lista viene vacia -> `PacienteNoEncontrado`
- [x] Cierre: `mapear_paciente(pacientes[0])` -> un solo `PacienteVista`, porque el endpoint exacto no devuelve conjuntos
- [x] Nombre `buscar_exacto`, paralelo a `buscar_similar` (no `obtener_exacto`)
- [x] Se acepta la duplicacion de las dos lineas de armado del body entre ambos metodos (regla de tres)

Validacion de `buscar_exacto` (CERRADA):

- [x] `Patient` suelto -> 1 `PacienteVista` con `nombre_completo` "Juan Perez" y documento `CC 12345678`
- [x] El cliente falso registra el path y se confirma `/Patient/$consultar-paciente-exacto` (el similar usa `/rda/Patient/...`)
- [x] Los 5 casos de `_consultar` y las pruebas de `buscar_similar` siguen pasando

Cierre del incremento (CERRADO):

- [x] `servicio = PacienteService(fhir)` a nivel de modulo, al final del archivo (la clase se define antes de instanciarse)
- [x] `from app.core.http_client import fhir` en la cabecera
- [x] Verificado: `type(servicio).__name__ == "PacienteService"`, `_cliente` es `FHIRHttpClient` y `callable(servicio._token)` es `True`
- [x] Verificado: `dir(PacienteService)` -> `['_consultar', 'buscar_exacto', 'buscar_similar']`
- [x] Importar el modulo **no** dispara una llamada a Azure (el default guarda la funcion)
- [ ] Prueba real contra el APIM con datos ficticios, una vez (opcional, ya no bloquea el cierre)

Decisiones de diseno (cerradas):

- El servicio es la unica capa que conoce la red; el mapper no hace HTTP.
- Dos excepciones de dominio distintas: transporte/formato vs. "no vino ningun paciente".
- `try` angostos: uno por operacion que puede fallar (la llamada y el parseo JSON).
- Exito = familia **2xx**, no `== 200`.
- Mensaje de error con status + `path` + `response.text[:300]` (recortado, nunca completo).
- `raise ... from e` en toda traduccion de excepcion, para conservar la causa original.
- `_consultar` es privado: nadie fuera de la clase lo llama.
- El `path` sale de `settings` dentro del servicio: el router nunca ve endpoints del mecanismo.
- Inyeccion de dependencias con valor por defecto: la dependencia real es el default; las pruebas la reemplazan.
- El router de 0.5 solo importara `servicio`; no sabra nada de Azure, tokens ni `fhir`.
- `servicio` es una instancia unica de modulo (singleton practico de Python): conserva la cache de token del `token_manager` y la configuracion del cliente HTTP.

Errores de aprendizaje documentados (0.4):

- [x] `except` de red que usaba `response` -> `UnboundLocalError`: si `post` falla, `response` nunca se asigna
- [x] Condicion de status invertida (`if status in (2xx): raise`)
- [x] Enumerar codigos de exito en una tupla es fragil; la familia 2xx es el contrato
- [x] `except HTTPError` no atrapa `Timeout` ni `ConnectionError`: son hermanos, no hijos
- [x] `from e` conserva el traceback original; sin el, el mensaje dice "During handling..."
- [x] Anidacion: la `def` de un metodo va a 4 espacios y su cuerpo a 8. Sin la linea `class`, todo parece plano
- [x] Diferencia entre la funcion `obtener_token_valido` y su resultado `obtener_token_valido()`
- [x] Pydantic v2 no acepta argumentos posicionales en el constructor: usar siempre `campo=valor`
- [x] Un `"""..."""` que no es la primera linea de la funcion no es docstring: para separar bloques, usar `#`
- [x] El `if __name__ == "__main__":` va al final del archivo; las funciones se definen antes de usarse (Python lee de arriba abajo)
- [x] Nombrar el parametro igual que el campo del esquema evita dos nombres para el mismo dato
- [x] Un valor por defecto que es una **funcion** se escribe sin parentesis: con parentesis se ejecuta al importar
- [x] `servicio = PacienteService(fhir)` va despues de la clase: Python lee de arriba abajo y si no, `NameError`
- [x] Diferencia entre "el nombre de la funcion" (`__defaults__` lo muestra como `<function ...>`) y "su resultado"
- [x] Un cliente falso que ignora el `path` da una falsa sensacion de seguridad: registrar `paths` convierte la prueba en una verificacion real del endpoint
- [x] Patrones en uso: arquitectura en capas, inyeccion de dependencias, adaptador (capa anticorrupcion) y fachada. No hay MVC ni Repository porque no hay base de datos

---

## QUE FALTA

### 0.5 - API + UI (SIGUIENTE)

Objetivo: exponer el servicio en una pantalla web minima (buscar por documento y ver resultados), sin que el router sepa nada de FHIR.

- [ ] `app/api/routers/pacientes.py` (archivo existe pero esta vacio)
  - [ ] `GET /pacientes` -> formulario de busqueda (HTML)
  - [ ] `GET /pacientes/buscar` (o `POST`) -> llama `servicio.buscar_similar(...)` y renderiza una lista
  - [ ] Traducir `PacienteNoEncontrado` y `ErrorConsultaIHCE` a mensajes de pantalla (no tracebacks)
  - [ ] `GET /pacientes/{tipo}/{numero}` -> `servicio.buscar_exacto(...)` y ficha del paciente
- [ ] `app/api/routers/home.py` (archivo existe pero esta vacio)
  - [ ] `GET /` -> redireccion o portada
- [ ] `app/templates/base.html` (archivo existe pero esta vacio) y plantillas en `pages/`, `partials/`, `components/` (carpetas vacias)
  - [ ] `base.html` con daisyUI y bloque `{% block contenido %}`
  - [ ] partial de resultados reutilizable (HTMX) y partial de mensaje de error
- [ ] Registrar routers en `app/main.py`, montar Jinja2 y estaticos
- [ ] El router solo importa `servicio`; nunca `fhir`, ni `settings`, ni `obtener_token_valido`

Criterio de cierre: abrir la app en el navegador, buscar un documento ficticio y ver la ficha o el mensaje de "no encontrado", sin tocar el servicio.

### Pendientes transversales

- [x] Quitar el `print("revisando:", ...)` de `_valor_extension`
- [x] Corregir estilo: `def _documento (` -> `def _documento(`
- [x] Eliminar imports muertos en `paciente_service.py`
- [x] Commit del incremento 0.3 (`6369381`)
- [ ] Normalizar `birthDate` a `YYYY-MM-DD` en el mapper (FHIR permite `2026-11` y `2026`)
- [x] Confirmar que `.env` sigue fuera de Git (verificado: no aparece en `git ls-files`)
- [ ] Decidir si `app/schemas/fhir/` (creado y vacio) se usa para modelos FHIR o se elimina
- [x] Convencion de commits retomada: `1dda2f6` y `60b1393` usan prefijo
- [ ] **`paciente_service.py` linea 5**: importa `consultar_paciente_exacto` y `consultar_paciente_similar` de `app/integrations/ihce/patient.py`, pero ya nadie los usa. Hay que borrar esa linea antes del commit de 0.4. Despues queda decidir si `patient.py` se reduce a constantes o se elimina
- [ ] Convertir `probar_consultar.py` en `tests/test_paciente_service.py` con `pytest` y `parametrize` (incremento propio, no mezclar con 0.4)
- [x] Commit de limpiezas de codigo: `1dda2f6`
- [x] `probar_consultar.py` versionado: `60b1393`
- [ ] Commit de cierre de 0.4: `feat(ihce): add buscar_exacto and shared service instance` + `test:` + `docs:` (en ese orden)
- [ ] Commit de esta actualizacion de `ESTADO.md` (`docs:`)

---

## Contrato de vista de paciente (CERRADO)

| Campo vista | Origen FHIR | Regla |
| :-- | :-- | :-- |
| id_paciente | Patient.id | directo |
| tipo_documento | identifier[].type.coding[].code | solo coding con system `https://fhir.minsalud.gov.co/rda/CodeSystem/ColombianPersonIdentifier`; si falta -> None |
| numero_documento | identifier[].value | del identifier elegido (preferir use=official) |
| primer_nombre | name[use=official].given[0] | fallback: primer name |
| segundo_nombre | given[1:] unido con espacio | None si vacio |
| primer_apellido | _family.extension[ExtensionFathersFamilyName].valueString | fallback: family completo |
| segundo_apellido | _family.extension[ExtensionMothersFamilyName].valueString | fallback: None |
| fecha_nacimiento | Patient.birthDate | directo YYYY-MM-DD (normalizacion pendiente) |
| sexo | Patient.gender | codigo crudo, sin traducir |
| nombre_completo | propiedad calculada | concatenacion de nombres y apellidos |

Reglas: no usar `coding[0]` a ciegas; no partir `family` por espacios.

URLs confirmadas:

- `https://fhir.minsalud.gov.co/rda/StructureDefinition/ExtensionFathersFamilyName` -> apellido paterno
- `https://fhir.minsalud.gov.co/rda/StructureDefinition/ExtensionMothersFamilyName` -> apellido materno
- `https://fhir.minsalud.gov.co/rda/CodeSystem/ColombianPersonIdentifier` -> tipo de documento colombiano

---

## Como retomar

1. Leer este archivo y `PROMPT_MENTOR.md`.
2. Validar que el entorno sigue sano:

```bash
py -c "from app.services.paciente_service import PacienteService, ErrorConsultaIHCE, PacienteNoEncontrado; from app.integrations.ihce.paciente_mapper import mapear_paciente; print('IMPORTS OK')"
```

3. Confirmar que la clase expone lo esperado:

```bash
py -c "from app.services.paciente_service import PacienteService; print([n for n in dir(PacienteService) if not n.startswith('__')])"
```

Resultado esperado hoy: `['_consultar', 'buscar_exacto', 'buscar_similar']`.

Comprobar tambien la instancia compartida:

```bash
py -c "from app.services.paciente_service import servicio; print(type(servicio).__name__, '|', type(servicio._cliente).__name__); print('token es funcion:', callable(servicio._token))"
```

Resultado esperado: `PacienteService | FHIRHttpClient` y `token es funcion: True`.

4. Re-ejecutar la validacion del servicio si se toco:

```bash
py probar_consultar.py
```

5. Continuar por **0.5 - API + UI**: router de pacientes, router de home, plantillas y registro en `main.py`.

---

## Notas

- Usar siempre `README_VISOR_IHCE_GESTION_FARMACEUTICA.md`, `PROMPT_MENTOR.md` y `ESTADO.md` al retomar sesion
- Ir un paso a la vez; un incremento pequeno por turno
- Mantener coherencia con `AutomatedUatIHCE`
- Codigo minimo, explicar primero, preguntar si hay duda
- El mapper debe vivir en `app/integrations/ihce/`, no en el modelo de vista ni en el router: es capa anticorrupcion de protocolo
- `mapear_paciente` no hace HTTP: recibe un `Patient` ya descargado. La red es responsabilidad del servicio.
- `identifier` es 0..* y puede venir vacio: nunca indexar `[0]` sin comprobar
- `name` es 0..*: filtrar por `use=official` y caer al primero solo como fallback
- La fuente es autoritativa (maestro de personas / RNEC), pero "autoritativo" no implica "siempre completo": el fallback cubre ausencia, no desconfianza
- Mientras se trabaja en REPL, reiniciar el interprete tras editar un modulo ya importado
- Un metodo no se da por cerrado hasta que tiene su prueba con cliente falso (sin red)
