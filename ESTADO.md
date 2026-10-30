# ESTADO DEL PROYECTO - Visor IHCE + Gestión Farmacéutica Colombia

## Última actualización
Fecha: 2026-10-30

## Resumen de un vistazo

| Incremento | Estado |
| :-- | :-- |
| 0.1 Infraestructura base (config, auth, HTTP, /health) | CERRADO |
| 0.2 Cliente IHCE + contrato de vista de paciente | CERRADO |
| 0.3 Mapper `Patient -> PacienteVista` | NO INICIADO |
| 0.4 Servicio de pacientes (Bundle -> lista de vistas) | NO INICIADO |
| 0.5 API + UI (router y plantillas) | NO INICIADO |

Ultima accion realizada: validacion manual en REPL del flujo real (token + `$consultar-paciente-similar` + lectura del `Patient` devuelto).

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
- [x] Git inicializado
- [x] `app/main.py` con `GET /health`
- [x] Validado con uvicorn: `/health` y `/docs` responden

### 0.2 - Cliente IHCE y contrato de vista (CERRADO)

Codigo:

- [x] `app/integrations/ihce/patient.py` con `consultar_paciente_similar()` y `consultar_paciente_exacto()`, usando `fhir.post(token, path, json_body=...)`
- [x] `app/schemas/request/paciente_request.py` con `ConsultaPacienteSimilar` y `ConsultaPacienteExacto` (ambos con `usuario_humano` y `crear_json_fhir()`)
- [x] `app/schemas/view/paciente_view.py` con `PacienteVista` (9 campos, todos `Optional[str]`)

Validaciones realizadas:

- [x] `obtener_token_valido()` devuelve un token `str` valido contra el tenant
- [x] `crear_json_fhir()` genera un `Parameters` identico al body usado en Postman (`identifier.part` + `humanuser`)
- [x] La llamada real a `$consultar-paciente-similar` devuelve un `Bundle` con recursos `Patient`
- [x] `$consultar-paciente-exacto` devuelve un `Patient` suelto, no un `Bundle`
- [x] El `Bundle` puede traer mas de un paciente

Hallazgos de estructura real del `Patient` (documentados, no inventados):

- [x] `name[]`: `use` (`official`), `family` concatenado (`"TORRES ARDILA"`), `_family.extension[]` con `ExtensionFathersFamilyName` (`TORRES`) y `ExtensionMothersFamilyName` (`ARDILA`), `given[]` ordenado (`["DIEGO","ARMANDO"]`)
- [x] `identifier[]`: `use` (`official`), `type.coding[]` con dos codings (`v2-0203/PN` generico y `ColombianPersonIdentifier/CC`), `system` RNEC y `value`
- [x] Contrato de mapeo `Patient -> PacienteVista` cerrado (ver seccion siguiente)

---

## QUE FALTA

### 0.3 - Mapper `Patient -> PacienteVista` (NO INICIADO)

- [ ] 0.3.1 Agregar `@property nombre_completo` a `PacienteVista`
- [ ] 0.3.2 Crear `app/integrations/ihce/paciente_mapper.py` con las URLs de extension y CodeSystem como constantes
- [ ] 0.3.3 Extraer apellidos desde `_family.extension` (con fallback a `family`)
- [ ] 0.3.4 Extraer nombres desde `given[]`
- [ ] 0.3.5 Extraer `identifier` (filtrar por CodeSystem colombiano, preferir `use=official`)
- [ ] 0.3.6 Ensamblar el `PacienteVista` completo y validarlo contra el `Patient` real ya obtenido (sin volver a llamar al mecanismo)

### 0.4 - Servicio de pacientes (NO INICIADO)

- [ ] Servicio que recorra `Bundle.entry[]`, aplique el mapper y devuelva `list[PacienteVista]`
- [ ] Manejo explicito de `Bundle` vacio (`total = 0`)
- [ ] Manejo explicito de error HTTP y de respuesta no JSON

### 0.5 - API + UI (NO INICIADO)

- [ ] `app/api/routers/pacientes.py` (archivo existe pero esta vacio)
- [ ] `app/api/routers/home.py` (archivo existe pero esta vacio)
- [ ] `app/templates/base.html` (archivo existe pero esta vacio) y plantillas en `pages/`, `partials/`, `components/` (carpetas vacias)
- [ ] Registrar routers en `app/main.py` y montar Jinja2/estaticos

### Pendientes transversales

- [ ] Commit de los cambios actuales (`ESTADO.md`, `PROMPT_MENTOR.md`, `app/integrations/ihce/patient.py`, `app/schemas/request/`, `app/schemas/view/paciente_view.py`)
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
py -c "from app.schemas.request.paciente_request import ConsultaPacienteSimilar, ConsultaPacienteExacto; from app.schemas.view.paciente_view import PacienteVista; print('IMPORTS OK')"
```

3. Continuar por **0.3.1** (`@property nombre_completo`).

---

## Notas

- Usar siempre `README_VISOR_IHCE_GESTION_FARMACEUTICA.md`, `PROMPT_MENTOR.md` y `ESTADO.md` al retomar sesion
- Ir un paso a la vez; un incremento pequeno por turno
- Mantener coherencia con `AutomatedUatIHCE`
- Codigo minimo, explicar primero, preguntar si hay duda
- La validacion funcional de `AutomatedUatIHCE/features/patient.feature` paso: 3 escenarios y 12 pasos sin fallos
- Esa prueba solo valida `resourceType == "Bundle"`; no valida los campos internos del paciente
- El mapper debe vivir en `app/integrations/ihce/`, no en el modelo de vista ni en el router: es capa anticorrupcion de protocolo
- `identifier` es 0..* y puede venir vacio: nunca indexar `[0]` sin comprobar
- `name` es 0..*: filtrar por `use=official` y caer al primero solo como fallback
- El status code de la llamada real no quedo anotado explicitamente; la validacion fue funcional (devolvio datos)
