from pydantic import BaseModel

class ConsultaPacienteSimilar(BaseModel):
    """
    Modelo para la operación 'consultar-paciente-similar'.
    """
    tipo_documento: str
    numero_documento: str
    usuario_humano: str

    def crear_json_fhir(self)->dict:
        # Esta es la estructura que definimos basada en el estándar IHCE
        return {
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "identifier",
                        "part": [
                            {
                                "name": "type",
                                "valueString": self.tipo_documento
                            },
                            {
                                "name": "value",
                                "valueString": self.numero_documento
                            }
                        ]
                    },
                    {
                        "name": "humanuser",
                        "valueString": self.usuario_humano
                    }
                ]
            }


class ConsultaPacienteExacto(BaseModel):
    """
    Modelo para la operación 'consultar-paciente-exacto'.
    """
    tipo_documento: str
    numero_documento: str
    usuario_humano: str

    def crear_json_fhir(self) -> dict:
        return {
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "identifier",
                        "part": [
                            {
                                "name": "type",
                                "valueString": self.tipo_documento
                            },
                            {
                                "name": "value",
                                "valueString": self.numero_documento
                            }
                        ]
                    },
                    {
                        "name": "humanuser",
                        "valueString": self.usuario_humano
                    }
                ]
            }