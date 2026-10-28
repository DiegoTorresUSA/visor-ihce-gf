import os
from pydantic import Field # Importamos Field para los alias
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    """
    Esta clase valida que todas las variables del .env existan.
    Si falta una, el programa se detendrá con un error claro.
    """
    
    # 1. Detectamos el ambiente
    ENVIRONMENT: str = os.getenv("APP_ENV", "uat_qas").lower()

    # 2. Definimos las variables obligatorias
    TENANT_ID: str = Field(validation_alias="IHCE_TENANT_ID")
    CLIENT_ID: str = Field(validation_alias="IHCE_CLIENT_ID")
    CLIENT_SECRET: str = Field(validation_alias="IHCE_CLIENT_SECRET")
    SCOPE: str = Field(validation_alias="IHCE_SCOPE")
    APIM_URL: str # Este se llama igual, no necesita alias
    APIM_SUBSKEY: str = Field(validation_alias="IHCE_APIM_SUBS_KEY")
    API_KEY: str # Este también se llama igual
    IHCE_CONSULTAR_PACIENTE_SIMILAR: str = Field(validation_alias="IHCE_CONSULTAR_PACIENTE_SIMILAR")
    IHCE_CONSULTAR_PACIENTE_EXACTO: str = Field(validation_alias="IHCE_CONSULTAR_PACIENTE_EXACTO")
    IHCE_CONSULTAR_PRACTITIONER: str = Field(validation_alias="IHCE_CONSULTAR_PRACTITIONER")
    IHCE_CONSULTAR_ORGANIZATION: str = Field(validation_alias="IHCE_CONSULTAR_ORGANIZATION")
    IHCE_CONSULTAR_EAPB: str = Field(validation_alias="IHCE_CONSULTAR_EAPB")
    IHCE_CONSULTAR_INMUNIZACION: str = Field(validation_alias="IHCE_CONSULTAR_INMUNIZACION")
    IHCE_CONSULTAR_CODESYSTEM: str = Field(validation_alias="IHCE_CONSULTAR_CODESYSTEM")
    IHCE_CODESYSTEM_LOOKUP: str = Field(validation_alias="IHCE_CODESYSTEM_LOOKUP")
    IHCE_CODESYSTEM_SINCE: str = Field(validation_alias="IHCE_CODESYSTEM_SINCE")
    IHCE_CONSULTAR_PACIENTE_RDA: str = Field(validation_alias="IHCE_CONSULTAR_PACIENTE_RDA")
    IHCE_CONSULTAR_PACIENTE_ENCUENTROS: str = Field(validation_alias="IHCE_CONSULTAR_PACIENTE_ENCUENTROS")
    IHCE_CONSULTAR_DOCUMENT_REFERENCE_QUERY: str = Field(validation_alias="IHCE_CONSULTAR_DOCUMENT_REFERENCE_QUERY")
    IHCE_CONSULTAR_DOCUMENT_COMPOSITION: str = Field(validation_alias="IHCE_CONSULTAR_DOCUMENT_COMPOSITION")
    IHCE_CONSULTAR_DOCUMENT_REFERENCE: str = Field(validation_alias="IHCE_CONSULTAR_DOCUMENT_REFERENCE")
    IHCE_DESCARGAR_PDF_DOCUMENT_REFERENCE: str = Field(validation_alias="IHCE_DESCARGAR_PDF_DOCUMENT_REFERENCE")
    IHCE_GENERAR_RESUMEN_LONGITUDINAL: str = Field(validation_alias="IHCE_GENERAR_RESUMEN_LONGITUDINAL")
    IHCE_CONSULTAR_RESUMEN_LONGITUDINAL: str = Field(validation_alias="IHCE_CONSULTAR_RESUMEN_LONGITUDINAL")
    IHCE_ENVIAR_RDA_PACIENTE:str = Field(validation_alias="IHCE_ENVIAR_RDA_PACIENTE")
    IHCE_ENVIAR_RDA_CONSULTA_EXTERNA:str = Field(validation_alias="IHCE_ENVIAR_RDA_CONSULTA_EXTERNA")
    IHCE_ENVIAR_RDA_HOSPITALIZACION:str = Field(validation_alias="IHCE_ENVIAR_RDA_HOSPITALIZACION")
    IHCE_ENVIAR_RDA_URGENCIAS:str = Field(validation_alias="IHCE_ENVIAR_RDA_URGENCIAS")
    IHCE_NOTA_ACLARATORIA:str = Field(validation_alias="IHCE_NOTA_ACLARATORIA")

    # 3. Propiedad calculada
    @property
    def AUTH_URL(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/token"

# 4. Configuración para leer los archivos .env automáticamente
    model_config = SettingsConfigDict(
        env_file=(f".env.{os.getenv('APP_ENV', 'uat_qas').lower()}", ".env"),
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variables no definidas en la clase
    )


settings = Settings()
