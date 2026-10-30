from pydantic import BaseModel
from typing import Optional

class PacienteVista(BaseModel):
    """
        Modelo de vista para mostrar información del paciente en el visor.
        Se construye a partir de la respuesta FHIR del mecanismo IHCE.
    """
    id_paciente: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    primer_nombre: Optional[str] = None
    segundo_nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None