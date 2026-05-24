from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.connection import engine, Base
from app.routes.address_routes import router as address_router
from app.exceptions.handlers import register_exception_handlers
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the FastAPI application.
    Auto-creates database tables on startup.
    """
    logger.info("Starting up Address Book application...")
    try:
        # Ensure database tables exist at start
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/checked successfully.")
    except Exception as e:
        logger.critical(f"Failed to bootstrap database schemas: {e}", exc_info=True)
        raise e
    yield
    logger.info("Shutting down Address Book application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-ready FastAPI Address Book API featuring geopy oblate-spheroid distance queries.",
    lifespan=lifespan
)

# Initialize global custom exception filters
register_exception_handlers(app)

# Register versioned address book endpoints
app.include_router(address_router, prefix=f"{settings.API_V1_STR}/addresses", tags=["Addresses"])

@app.get("/health", tags=["System"], summary="API operational status check")
def health_check() -> dict:
    """Returns the operational status of the service."""
    return {"status": "healthy"}
