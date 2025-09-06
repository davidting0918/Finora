import logging
from argparse import ArgumentParser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from backend.analytics.router import router as analytics_router
from backend.auth.router import router as auth_router
from backend.core.environment import env_config, get_config
from backend.core.initializer import init_environment
from backend.transaction.router import router as transaction_router
from backend.user.router import router as user_router

# Configure logging based on environment
logging.basicConfig(
    level=getattr(logging, get_config("log_level")), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data based on current environment on startup"""
    logger.info(f"🚀 Starting Finora API in {env_config.environment.value} environment")
    await init_environment()
    yield
    logger.info("🛑 Shutting down Finora API")


# Create FastAPI application with environment-aware configuration
app = FastAPI(
    title="Finora API",
    description="A modern expense tracking platform with comprehensive financial management features",
    version="1.0.0",
    debug=get_config("debug"),
    lifespan=lifespan,
)

# Add CORS middleware with environment-specific origins
cors_origins = get_config("cors_origins")
logger.info(f"🌐 Configuring CORS for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Finora API!",
        "environment": env_config.environment.value,
        "version": "1.0.0",
        "debug": get_config("debug"),
    }


@app.get("/scalar")
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Scalar",
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
