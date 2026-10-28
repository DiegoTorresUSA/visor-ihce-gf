# Visor IHCE + Gestión Farmacéutica Colombia

## Objetivo

Crear un visor para el **Mecanismo de Interoperabilidad IHCE** con enfoque en **Gestión Farmacéutica**.

El propósito no es solo tenerlo funcional, sino **aprender de forma estructurada**: entender HL7 FHIR R4 aplicado al contexto colombiano, consumir el mecanismo tal como está implementado en `AutomatedUatIHCE`, diseñar con capas claras y lograr un front limpio, profesional y fácilmente evolucionable.

## Principios

- **Aprender antes de copiar**: Cada cambio se explica por el porqué, con alternativas, pros/contras y trade-offs.
- **Coherente con lo ya existente**: Reutilizamos el patrón de autenticación, token, cabeceras y configuración que ya funciona en `AutomatedUatIHCE`.
- **FHIR pragmático**: Solo trabajaremos los recursos/operaciones necesarios por caso de uso. Haremos `FHIR -> Modelo de Vista` para simplificar la información al usuario final.
- **Server-first, evolutivo**: Empezamos con renderizado del lado del servidor, pero con arquitectura por capas que permita migrar a una API pura + SPA sin reescribir la lógica de integración/transformación.
- **Incremental y testeable**: Un cambio a la vez, descompuesto, validable y entendible.
- **Profesional desde el inicio**: UI limpia, componentes reutilizables, tipado con Pydantic y código legible.

## Stack definido

### Backend
| Tecnología | Versión | Razón |
| :-- | :-- | :-- |
| [Python](https://www.python.org/) | 3.11+ | Base del proyecto. |
| [FastAPI](https://fastapi.tiangolo.com/) | Compatible | API moderna, tipado, Pydantic v2, validación, documentación automática en `/docs`. |
| [Uvicorn](https://www.uvicorn.org/) | [standard] | Servidor ASGI para desarrollo con `--reload`. |
| [Pydantic v2](https://docs.pydantic.dev/latest/) | >= 2.7.1 | Validación de datos, contratos y modelos de vista. |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | >= 2.2.1 | Gestión de configuración con `.env` y entornos, igual que `AutomatedUatIHCE`. |
| [requests](https://docs.python-requests.org/) | 2.31.0 | **Reutilizamos** `http_client`, `auth_client` y `token_manager` de `AutomatedUatIHCE`. Mantiene coherencia con OAuth2 + APIM + cabeceras. |
| [python-multipart](https://github.com/Kludex/python-multipart) | Última | Necesario para formularios HTML (búsqueda por tipo/número de documento). |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.0.1 | Carga de variables `.env` en desarrollo. |

### Frontend
| Tecnología | Uso | Razón |
| :-- | :-- | :-- |
| [Jinja2](https://jinja.palletsprojects.com/) | Plantillas SSR | Renderizado del lado del servidor. Nos obliga a pensar en "¿Qué datos necesito mostrar?" en lugar de armar todo con JSON. |
| [HTMX](https://htmx.org/) | Interactividad | Búsquedas, filtros, carga de detalle o fragmentos sin recargar toda la página. |
| [Alpine.js](https://alpinejs.dev/) | Estado local | Tabs, acordeones, modales, toggles. Ligero y se integra muy bien con HTML + HTMX. |
| [Tailwind CSS](https://tailwindcss.com/) | Estilos | Rápido, moderno y profesional. Permite lograr un UI limpio con pocas clases. |
| [daisyUI](https://daisyui.com/) | Componentes sobre Tailwind | Componentes semánticos (`card`, `table`, `badge`, `alert`, `input`, `tabs`) con muy buen aspecto. |
| [Lucide Icons](https://lucide.dev/) | Iconografía | Limpios, minimalistas y consistentes. |

> **Nota:** Empezaremos con **CDN** para HTMX, Alpine.js, Tailwind CSS, daisyUI y Lucide Icons. Sin Node al inicio. Cuando el proyecto tenga más vistas, podemos migrar a **Tailwind CLI** de forma incremental y explicada.

## Arquitectura propuesta

Mantendremos separación por capas. El objetivo es que `integrations/ihce/` y `services/` sean reutilizables si en algún momento queremos exponer solo una API REST pura.

```text
visor-ihce-gf/
├── app/
│   ├── __init__.py
│   ├── main.py                # Punto de entrada FastAPI (monta static/, templates/, routers)
│   │
│   ├── core/                  # INFRAESTRUCTURA COMÚN (heredada de AutomatedUatIHCE)
│   │   ├── __init__.py
│   │   ├── config.py          # pydantic-settings + lectura .env
│   │   ├── auth.py            # OAuth2 client_credentials (Azure AD)
│   │   ├── token_manager.py   # Caché de token + renovación ~60s antes de expirar
│   │   └── http_client.py     # requests + reintentos + backoff + headers IHCE/APIM
│   │
│   ├── integrations/          # CLIENTE DIRECTO AL MECANISMO IHCE
│   │   └── ihce/
│   │       ├── __init__.py
│   │       └── patient.py     # Operaciones $consultar-paciente-similar / $consultar-paciente-exacto
│   │
│   ├── schemas/               # CONTRATOS
│   │   ├── __init__.py
│   │   ├── fhir/              # (Opcional) Para entender estructuras FHIR
│   │   └── view/              # MODELOS DE VISTA (FHIR -> Vista para la UI)
│   │       └── paciente_view.py
│   │
│   ├── services/              # ORQUESTACIÓN + TRANSFORMACIÓN
│   │   ├── __init__.py
│   │   └── paciente_service.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/           # Routers para el visor (HTMX + vistas)
│   │       ├── __init__.py
│   │       ├── home.py
│   │       └── pacientes.py
│   │
│   ├── templates/             # Jinja2 SSR
│   │   ├── base.html          # Layout: Tailwind + daisyUI + HTMX + Alpine + Lucide (CDN)
│   │   ├── components/        # Parciales reutilizables (_navbar.html, _card_*.html, ...)
│   │   ├── pages/             # Vistas completas (home.html, paciente_detalle.html, ...)
│   │   └── partials/          # Fragmentos para HTMX (hx-target/hx-swap)
│   │
│   └── static/
│       ├── css/
│       │   └── app.css        # Reservado (para Tailwind CLI futuro)
│       ├── js/
│       │   └── app.js         # JS propio mínimo
│       └── img/               # Logos/recursos
│
├── .env                      # Copiar desde AutomatedUatIHCE (LOCAL - NO SUBIR A GIT)
├── .env.example              # Plantilla con nombres de variables sin valores
├── requirements.txt
└── README_VISOR_IHCE_GESTION_FARMACEUTICA.md
```

**Razón de esta estructura:** `core/` mantiene el mismo espíritu que `AutomatedUatIHCE`. `integrations/ihce/` aísla el consumo directo al mecanismo. `services/` es el puente entre FHIR y el modelo de vista. `templates/` se organiza por `components/`, `pages/` y `partials/` para mantenerlo modular y fácil de evolucionar.

## Metodología de trabajo

Para **CADA** tarea/feature seguiremos este flujo rigurosamente:

| Paso | Nombre | Objetivo |
| :-- | :-- | :-- |
| **1** | **OBJETIVO** | ¿Qué vamos a lograr y para qué? |
| **2** | **CONCEPTOS** | Teoría necesaria (FHIR, OAuth2, APIM, arquitectura, etc.). Solo lo justo y necesario. |
| **3** | **ANÁLISIS** | Revisar código existente relevante (`AutomatedUatIHCE`) y ver cómo encaja con el visor. |
| **4** | **ALTERNATIVAS** | Mínimo 2 alternativas con pros/contras y trade-offs. |
| **5** | **DISEÑO** | Propuesta concreta: archivos, funciones, contratos, flujo y diagrama si aplica (Mermaid/C4). |
| **6** | **IMPLEMENTACIÓN GUIADA** | Código paso a paso. Explico imports, líneas relevantes y decisiones. Solo lo necesario para el paso actual. |
| **7** | **VALIDACIÓN** | Cómo probarlo (`/docs`, navegador, curl/httpie). Errores comunes, debugging y cómo solucionarlos. |
| **8** | **APRENDIZAJE** | Ejercicio corto para reforzar + preguntas para autoevaluación. |
| **9** | **SIGUIENTE PASO** | Sugerencia clara del siguiente incremento. |

## Roadmap inicial (incremental)

| Incremento | Tarea | Estado | Comentario |
| :-- | :-- | :-- | :-- |
| **0.1** | **Scaffolding + Infra IHCE** | Pendiente | Crear estructura. Copiar/reutilizar `core/` desde `AutomatedUatIHCE` ajustando imports. Copiar `.env` localmente. Crear `requirements.txt`, `app/main.py` con `GET /health`. Validar configuración, obtención de token y conectividad al mecanismo. |
| **0.2** | **Búsqueda de paciente directo al mecanismo** | Pendiente | `integrations/ihce/patient.py` con `$consultar-paciente-similar`/`$consultar-paciente-exacto`. `schemas/view/paciente_view.py` (modelo de vista). `services/paciente_service.py` (orquestación + `FHIR -> Modelo de Vista`). Router + primera vista HTML con buscador. Probar contra el mecanismo real. |
| **0.3** | **Detalle del paciente + contexto clínico** | Pendiente | Mostrar paciente seleccionado, encuentros/atenciones, DocumentReference/Composition. Crear componentes reutilizables en `templates/components/` y fragmentos HTMX en `templates/partials/`. Mantener UI limpia con Tailwind + daisyUI. |
| **0.4** | **Gestión Farmacéutica** | Pendiente | Enfocarnos en lo relacionado a prescripción/dispensación según lo que exponga el mecanismo. Aprender terminología colombiana (CUM, ATC) cuando sea necesario. Transformar FHIR a vistas claras para apoyo a gestión farmacéutica. |
| **0.5** | **Refactor, componentes y pulido** | Pendiente | Consolidar parciales, limpiar capas, revisar imports, añadir test mínimo con `pytest` para `services/`/mapeos, y pulir la UI sin complejizar. |

## Cómo arrancar

Sigue este orden. **Tú armas las carpetas/archivos**. Yo te guío paso a paso con la metodología.

1. **Estructura** - Crea las carpetas y `__init__.py` tal como se muestra arriba.
2. **Base infra** - Copia `core/config.py`, `core/auth.py`, `core/token_manager.py`, `core/http_client.py` desde `C:\Users\MANDO\Documents\AutomatedUatIHCE\` ajustando imports para `app.core.*`.
3. **Variables** - Copia `.env` desde `AutomatedUatIHCE` a la raíz de `visor-ihce-gf/`. Crea `.env.example` con las mismas claves pero sin valores. **Nunca commitear `.env`**.
4. **Dependencias** - Crea `requirements.txt` con el stack backend definido.
5. **App mínima** - Crea `app/main.py` con FastAPI, montaje de `static/` y `templates/`, y endpoint `GET /health`.
6. **Layout base** - Crea `templates/base.html` con Tailwind CSS + daisyUI + HTMX + Alpine.js + Lucide Icons vía CDN.
7. **Validación** - Levanta con `uvicorn app.main:app --reload`, revisa `/docs`, prueba `GET /health` y valida obtención de token.
8. **Continuar** - Con eso validado, pasamos al **Incremento 0.2** (búsqueda de paciente directo al mecanismo).

## Referencias

| Referencia | Uso |
| :-- | :-- |
| [`AutomatedUatIHCE`](C:\Users\MANDO\Documents\AutomatedUatIHCE) | **Base obligatoria**. Aquí están el flujo OAuth2, `token_manager`, `http_client` con headers APIM, configuración y todas las operaciones IHCE que vamos a reutilizar. |
| [HL7 FHIR R4](https://hl7.org/fhir/R4/) | Referencia para entender recursos, `Parameters`, `Bundle`, operaciones `$...` cuando los encontremos. |
| [FastAPI Docs](https://fastapi.tiangolo.com/) | Para estructura, routers, dependencias, etc. |

**Regla de oro:** Coherentes con `AutomatedUatIHCE`, server-first con visión evolutiva, FHIR pragmático y aprendizaje estructurado. Un paso a la vez.
