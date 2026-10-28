from fastapi import FastAPI

app = FastAPI(
    title="Visor IHCE + Gestion Farmaceutica - Colombia",
    description="Visor para consumo del Mecanismo de Interoperabilidad IHCE",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "visor-ihce-gf"}