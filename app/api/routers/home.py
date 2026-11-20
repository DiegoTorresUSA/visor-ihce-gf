from fastapi import APIRouter, Request
from app.core.templates import templates
router = APIRouter()

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "pages/home.html", {})