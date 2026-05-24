from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger

class AddressNotFoundError(Exception):
    """Custom exception raised when a requested Address record does not exist."""
    def __init__(self, address_id: int):
        self.address_id = address_id
        super().__init__(f"Address with ID {address_id} was not found")

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom and override exception handlers globally in the FastAPI app.
    Translates raw exceptions into clean JSON responses and logs the events.
    """
    @app.exception_handler(AddressNotFoundError)
    async def address_not_found_handler(request: Request, exc: AddressNotFoundError) -> JSONResponse:
        logger.warning(f"Address lookup failed for path {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            # Format target location path beautifully
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg")
            errors.append({"field": loc, "message": msg})
        
        logger.warning(f"Validation validation failed on {request.method} {request.url.path}: {errors}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error at boundary", "errors": errors}
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(
            f"Database anomaly caught during request {request.method} {request.url.path}: {exc}", 
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database persistence error occurred. Please retry later."}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unexpected system crash caught during request {request.method} {request.url.path}: {exc}", 
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected system exception occurred."}
        )
