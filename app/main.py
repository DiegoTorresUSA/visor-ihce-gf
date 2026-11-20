from fastapi import FastAPI

from app.api.routers import home, pacientes

app = FastAPI(
    title="Visor IHCE + Gestion Farmaceutica - Colombia",
    description="Visor para consumo del Mecanismo de Interoperabilidad IHCE",
    version="0.1.0",
)

app.include_router(home.router)
app.include_router(pacientes.router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "visor-ihce-gf"}

