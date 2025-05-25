try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for routes, handling missing tags gracefully"""
    try:
        if route.tags and len(route.tags) > 0:
            return f"{route.tags[0]}-{route.name}"
        else:
            # Fallback for routes without tags
            return f"default-{route.name}"
    except (IndexError, AttributeError):
        # Handle any other edge cases
        return f"route-{route.name}"


if sentry_sdk and settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Configure CORS middleware
cors_origins = settings.all_cors_origins
# For local development, allow all origins
if settings.ENVIRONMENT == "local":  # pragma: no cover
    cors_origins = ["*"]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
