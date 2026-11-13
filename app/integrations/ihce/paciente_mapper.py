from app.schemas.view.paciente_view import PacienteVista

URL_APELLIDO_PATERNO = (
    "https://fhir.minsalud.gov.co/rda/StructureDefinition/ExtensionFathersFamilyName"
)

URL_APELLIDO_MATERNO = (
    "https://fhir.minsalud.gov.co/rda/StructureDefinition/ExtensionMothersFamilyName"
)

SISTEMA_TIPO_DOCUMENTO = (
    "https://fhir.minsalud.gov.co/rda/CodeSystem/ColombianPersonIdentifier"
)

def _elegir_nombre(nombres: list[dict]) -> dict:
    """
       Devuelve el HumanName marcado como oficial.
       Si ninguno lo está, devuelve el primero.
       Si la lista viene vacía, devuelve {}.
    """
    for nombre in nombres:
        if nombre.get("use") == "official":
            return nombre
    return nombres[0] if nombres else {}


def _valor_extension(extensiones: list[dict], url: str) -> str | None:
    """
        Devuelve el valueString de la extensión cuya url coincida.
        Si no existe, devuelve None.
    """
    for extension in extensiones:
        print("revisando:", extension.get("url"))
        if extension.get("url") == url:
            return extension.get("valueString")
    return None

def _apellidos(nombre: dict) -> tuple[str | None, str | None]:
    """
        Devuelve (primer_apellido, segundo_apellido).
        Usa las extensiones del perfil colombiano; si no existen,
        devuelve el family completo como primer apellido y None como segundo.
    """
    extensiones = nombre.get("_family", {}).get("extension", [])
    paterno = _valor_extension(extensiones, URL_APELLIDO_PATERNO)
    materno = _valor_extension(extensiones, URL_APELLIDO_MATERNO)

    if paterno is None and materno is None:
        return nombre.get("family"), None

    return paterno, materno

def _nombres(nombre: dict) -> tuple[str | None, str | None]:
    """
        Devuelve (primer_nombre, segundo_nombre) a partir de given[].
        Si hay más de dos, el resto se une con espacio en el segundo.
    """
    partes = nombre.get("given", [])
    if not partes:
        return None, None
    if len(partes) == 1:
        return partes[0], None
    return partes[0], " ".join(partes[1:])


def _documento (identifiers: list[dict]) -> tuple[str | None, str | None]:
    """
    Devuelve (tipo_documento, numero_documento).
    Prefiere los identifiers oficiales y el coding del CodeSystem colombiano.
    Si no hay coding colombiano, conserva el número pero deja el tipo en None.
    """
    oficiales = [i for i in identifiers if i.get("use") == "official"]
    otros = [i for i in identifiers if i.get("use") != "official"]
    candidatos = oficiales + otros

    for ident in candidatos:
        for coding in ident.get("type", {}).get("coding", []):
            if coding.get("system") == SISTEMA_TIPO_DOCUMENTO:
                return coding.get("code"), ident.get("value")

    if candidatos:
        return None, candidatos[0].get("value")

    return None, None


def mapear_paciente(patient:dict) -> PacienteVista:
    """
        Traduce un recurso Patient de FHIR a PacienteVista.
        No hace peticiones HTTP: recibe el recurso ya descargado.
    """
    nombre = _elegir_nombre(patient.get("name", []))
    primer_apellido, segundo_apellido = _apellidos(nombre)
    primer_nombre, segundo_nombre = _nombres(nombre)
    tipo_documento, numero_documento = _documento(patient.get("identifier", []))
    return PacienteVista(
        id_paciente = patient.get("id"),
        tipo_documento = tipo_documento,
        numero_documento = numero_documento,
        primer_nombre = primer_nombre,
        segundo_nombre = segundo_nombre,
        primer_apellido = primer_apellido,
        segundo_apellido = segundo_apellido,
        fecha_nacimiento = patient.get("birthDate"),
        sexo = patient.get("gender")
    )
