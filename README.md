# Visor IHCE + Gestión Farmacéutica Colombia

Visor clínico que consume el **Mecanismo de Interoperabilidad IHCE** del Ministerio de Salud y Protección Social de Colombia mediante **HL7 FHIR R4**, transforma los recursos FHIR en **modelos de vista** comprensibles y los presenta en una interfaz web limpia.

El proyecto se construye de forma incremental, priorizando que cada capa sea explicable, testeable y reutilizable. La integración (OAuth2 `client_credentials`, cabeceras APIM, caché de token y cliente HTTP con reintentos) sigue el mismo patrón ya validado en el proyecto de referencia `AutomatedUatIHCE`.

> **Estado:** en desarrollo activo. Hoy el proyecto resuelve autenticación, conexión al mecanismo y consulta de pacientes a nivel de backend. La interfaz web todavía no está implementada. Ver [Estado del proyecto](#estado-del-proyecto).

---

## Tabla de contenido

- [Objetivo](#objetivo)
- [Arquitectura](#arquitectura)
- [Flujo de una consulta](#flujo-de-una-consulta)
- [Stack](#stack)
- [Estado del proyecto](#estado-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [Ejecución](#ejecución)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Seguridad](#seguridad)
- [Documentación interna](#documentación-interna)
- [Hoja de ruta](#hoja-de-ruta)
- [Aviso](#aviso)

---

## Objetivo

Construir un visor que permita a un profesional de la salud consultar información de un paciente a través del mecanismo nacional de interoperabilidad, con énfasis en **gestión farmacéutica**.

Principios de diseño:

| Principio | Aplicación |
| :-- | :-- |
| **FHIR pragmático** | Solo se trabajan los recursos y operaciones que cada caso de uso necesita. La complejidad FHIR no se filtra a la interfaz. |
| **Separación de contratos** | `request` (lo que se envía al mecanismo) y `view` (lo que se muestra) son modelos distintos y no se mezclan. |
| **Capa anticorrupción** | El mapeo `FHIR -> Modelo de Vista` vive en `integrations/`, aislado del protocolo. |
| **Server-first evolutivo** | Renderizado en servidor con Jinja2 + HTMX; la lógica de integración queda lista para exponerse como API pura. |
| **Incremental** | Un cambio pequeño por vez, validado antes de continuar. |

## Arquitectura

```text
app/
├── core/                 # Infraestructura común
│   ├── config.py         # pydantic-settings + lectura de .env
│   ├── auth_client.py    # OAuth2 client_credentials (Azure AD)
│   ├── token_manager.py  # Caché de token con renovación anticipada
│   └── http_client.py    # Cliente HTTP con headers APIM, reintentos y backoff
│
├── integrations/ihce/    # Cliente directo al mecanismo IHCE
│   └── patient.py        # $consultar-paciente-similar / $consultar-paciente-exacto
│
├── schemas/
│   ├── request/          # Contratos de petición (Parameters FHIR)
│   ├── view/             # Modelos de vista para la UI
│   └── fhir/             # (reservado) Modelos de recursos FHIR
│
├── services/             # Orquestación y transformación FHIR -> vista
├── api/routers/          # Routers FastAPI
├── templates/            # Jinja2 (pages, partials, components)
└── static/               # CSS, JS e imágenes
```

| Capa | Responsabilidad | No debe |
| :-- | :-- | :-- |
| `core` | Configuración, autenticación, transporte HTTP | Conocer reglas de negocio |
| `integrations` | Hablar el protocolo del mecanismo (FHIR, APIM) y traducirlo | Renderizar o decidir presentación |
| `services` | Orquestar llamadas y devolver modelos de vista | Construir URLs o cabeceras |
| `schemas` | Definir contratos tipados | Contener lógica de red |
| `api` / `templates` | Exponer y presentar | Llamar directamente al mecanismo |

## Flujo de una consulta

```text
1. El visor recibe tipo y número de documento.
2. schemas/request construye el recurso Parameters (FHIR).
3. token_manager entrega un token vigente (o lo renueva).
4. integrations/ihce envía la petición con headers APIM.
5. El mecanismo responde un Bundle (búsqueda) o un Patient (exacto).
6. El mapper traduce Patient -> PacienteVista.
7. La plantilla muestra solo los campos del modelo de vista.
```

## Stack

**Backend**

| Tecnología | Uso |
| :-- | :-- |
| Python 3.11+ | Base del proyecto |
| FastAPI | API y renderizado de vistas, documentación automática en `/docs` |
| Uvicorn | Servidor ASGI de desarrollo |
| Pydantic v2 | Contratos, validación y modelos de vista |
| pydantic-settings | Configuración por entorno desde `.env` |
| requests | Cliente HTTP hacia APIM (mismo patrón que `AutomatedUatIHCE`) |
| python-multipart | Formularios HTML |

**Frontend** (previsto, vía CDN)

Jinja2 · HTMX · Alpine.js · Tailwind CSS · daisyUI · Lucide Icons

## Estado del proyecto

| Incremento | Alcance | Estado |
| :-- | :-- | :-- |
| 0.1 | Infraestructura base: configuración, OAuth2, cliente HTTP, `GET /health` | Completado |
| 0.2 | Cliente IHCE (`$consultar-paciente-similar` / `-exacto`) y contrato de vista de paciente | Completado |
| 0.3 | Mapper `Patient -> PacienteVista` | Siguiente |
| 0.4 | Servicio de pacientes (`Bundle -> list[PacienteVista]`) | Pendiente |
| 0.5 | Router + interfaz web (Jinja2 + HTMX + daisyUI) | Pendiente |

Validado contra el mecanismo real: obtención de token, construcción del `Parameters` y respuesta de `$consultar-paciente-similar` con un `Bundle` de recursos `Patient`.

## Requisitos

- Python 3.11 o superior
- Credenciales de acceso al mecanismo IHCE (tenant, client, secret, suscripción APIM)
- Git

## Instalación

```bash
git clone <url-del-repositorio>
cd visor-ihce-gf

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

Crear el archivo `.env` a partir de la plantilla:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS
```

Completar los valores con las credenciales reales del entorno de pruebas. **`.env` no se versiona.**

## Variables de entorno

La plantilla completa está en [`.env.example`](.env.example). Grupos principales:

| Grupo | Variables | Descripción |
| :-- | :-- | :-- |
| Identidad | `IHCE_TENANT_ID`, `IHCE_CLIENT_ID`, `IHCE_CLIENT_SECRET`, `IHCE_SCOPE` | Credenciales OAuth2 `client_credentials` de Azure AD |
| APIM | `APIM_URL`, `IHCE_APIM_SUBS_KEY`, `API_KEY` | URL base del API Management y llaves de suscripción |
| Operaciones | `IHCE_CONSULTAR_PACIENTE_SIMILAR`, `IHCE_CONSULTAR_PACIENTE_EXACTO`, ... | Rutas relativas de cada operación del mecanismo |
| Entorno | `APP_ENV` | Selecciona `.env.<entorno>` y `.env` |

Todas las variables son obligatorias: si falta alguna, la aplicación falla al iniciar con un error explícito (no hay valores por defecto silenciosos).

## Ejecución

```bash
uvicorn app.main:app --reload
```

| Recurso | URL |
| :-- | :-- |
| Health check | `http://127.0.0.1:8000/health` |
| Documentación interactiva | `http://127.0.0.1:8000/docs` |

Respuesta esperada de `/health`:

```json
{ "status": "ok", "service": "visor-ihce-gf" }
```

## Estructura del repositorio

| Archivo | Contenido |
| :-- | :-- |
| `ESTADO.md` | Bitácora de avance: qué está hecho, qué falta y cómo retomar |
| `PROMPT_MENTOR.md` | Reglas de mentoría y metodología de trabajo del proyecto |
| `README_VISOR_IHCE_GESTION_FARMACEUTICA.md` | Documento de diseño y decisiones originales |
| `.env.example` | Plantilla de variables de entorno sin valores |

## Seguridad

- `.env` está en `.gitignore` y **nunca** debe versionarse.
- No se registran tokens, credenciales ni datos clínicos en logs.
- Los ejemplos y pruebas usan datos ficticios o anonimizados.
- Si una credencial se expone, debe rotarse en Azure AD y en APIM de inmediato.

## Documentación interna

El proyecto se desarrolla con una metodología explícita (objetivo, conceptos, análisis, alternativas, diseño, implementación guiada, validación, aprendizaje y siguiente paso). El avance y las decisiones quedan registrados en `ESTADO.md` y `PROMPT_MENTOR.md`.

## Hoja de ruta

1. **Mapper `Patient -> PacienteVista`** con reglas explícitas para nombres, apellidos e identificadores.
2. **Servicio de pacientes** que recorra el `Bundle` y devuelva modelos de vista.
3. **Interfaz web** de búsqueda y detalle de paciente.
4. **Contexto clínico**: encuentros y documentos clínicos.
5. **Gestión farmacéutica**: prescripción y dispensación según lo que exponga el mecanismo.
6. **Pruebas** de mapeo y de servicios.

## Aviso

Proyecto con fines de aprendizaje y desarrollo técnico. Consume un entorno de pruebas del mecanismo nacional de interoperabilidad. **No debe usarse para decisiones clínicas** ni con datos de pacientes reales sin las autorizaciones, controles de acceso y cumplimiento normativo correspondientes (Ley 1581 de 2012 y normativa de historia clínica electrónica aplicable).
