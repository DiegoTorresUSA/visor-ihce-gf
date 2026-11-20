from fastapi import APIRouter, Request, Form
from app.core.templates import templates
from app.services.paciente_service import servicio
from app.core.config import settings

router = APIRouter(prefix="/pacientes", tags=["pacientes"])

@router.get("")
def formulario(request: Request):
    return templates.TemplateResponse(request, "pages/pacientes.html")

@router.post("/buscar")
def buscar(
    request: Request,
    tipo_documento:str = Form(...),
    numero_documento:str = Form(...),
):
    pacientes = servicio.buscar_similar(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        usuario_humano=settings.USUARIO_HUMANO,
    )

    return templates.TemplateResponse(request, "pages/pacientes.html", {
        "pacientes": pacientes,
    })