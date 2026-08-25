from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import CustomAPIException
from app.api.v1.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables for development/testing
    if settings.ENVIRONMENT in ["development", "test"]:
        await init_db()
    yield
    # Shutdown logic if required


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handlers
@app.exception_handler(CustomAPIException)
async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        errors.append({"field": loc, "message": err.get("msg")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": errors
            }
        }
    )


# Root landing endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
