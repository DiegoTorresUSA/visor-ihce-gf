# ESTADO DEL PROYECTO - Visor IHCE + Gestión Farmacéutica Colombia

## Última actualización
Fecha: 2026-11-04

## Resumen de un vistazo

| Incremento | Estado |
| :-- | :-- |
| 0.1 Infraestructura base (config, auth, HTTP, /health) | CERRADO |
| 0.2 Cliente IHCE + contrato de vista de paciente | CERRADO |
| 0.3 Mapper `Patient -> PacienteVista` | CERRADO |
| 0.4 Servicio de pacientes (Bundle -> lista de vistas) | NO INICIADO |
| 0.5 API + UI (router y plantillas) | NO INICIADO |

Ultima accion realizada: `mapear_paciente()` validado de punta a punta con datos ficticios (paciente completo y paciente vacio).

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

---

## QUE FALTA

### 0.4 - Servicio de pacientes (NO INICIADO)

- [ ] `app/services/paciente_service.py` con `buscar_paciente_similar(...)` -> `list[PacienteVista]`
- [ ] `app/services/paciente_service.py` con `consultar_paciente_exacto(...)` -> `PacienteVista`
- [ ] Recorrer `Bundle.entry[]` y aplicar `mapear_paciente` a cada `resource`
- [ ] Manejo explicito de `Bundle` vacio (`total = 0`)
- [ ] Manejo explicito de error HTTP y de respuesta no JSON (sin `except` amplios)

### 0.5 - API + UI (NO INICIADO)

- [ ] `app/api/routers/pacientes.py` (archivo existe pero esta vacio)
- [ ] `app/api/routers/home.py` (archivo existe pero esta vacio)
- [ ] `app/templates/base.html` (archivo existe pero esta vacio) y plantillas en `pages/`, `partials/`, `components/` (carpetas vacias)
- [ ] Registrar routers en `app/main.py` y montar Jinja2/estaticos

### Pendientes transversales

- [ ] Quitar el `print("revisando:", ...)` de depuracion en `_valor_extension`
- [ ] Corregir estilo: `def _documento (identifiers...)` -> `def _documento(identifiers...)`
- [ ] Commit del incremento 0.3
- [ ] Confirmar que `.env` sigue fuera de Git
- [ ] `app/schemas/fhir/` esta creado pero vacio: decidir si se usa para modelos de recursos FHIR o se elimina

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
| fecha_nacimiento | Patient.birthDate | directo YYYY-MM-DD |
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
py -c "from app.schemas.request.paciente_request import ConsultaPacienteSimilar, ConsultaPacienteExacto; from app.schemas.view.paciente_view import PacienteVista; from app.integrations.ihce.paciente_mapper import mapear_paciente; print('IMPORTS OK')"
```

3. Continuar por **0.4** (servicio de pacientes).

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
