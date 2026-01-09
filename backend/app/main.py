from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200", "http://localhost"], # Permitir frontend local y docker
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(routes.router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Iniciando API...")
        # Pre cargar modelos al iniciar la aplicación, para evitar que el primer request sea lento.
        from app.services.model_loader import ModelLoader
        try:
            logger.info("Pre-cargando modelo BETO CLS...")
            ModelLoader.get_beto_cls()
            logger.info("Pre-cargando modelo SBERT...")
            ModelLoader.get_sbert()
            logger.info("Pre-cargando modelo BETO NER...")
            ModelLoader.get_beto_ner()
            logger.info("Todos los modelos han sido cargados exitosamente.")
        except Exception as e:
            logger.error(f"Error durante la pre-carga de modelos: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
