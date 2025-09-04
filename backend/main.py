from argparse import ArgumentParser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from backend.analytics.router import router as analytics_router
from backend.auth.router import router as auth_router
from backend.core.initializer import init_category
from backend.transaction.router import router as transaction_router
from backend.user.router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize categories on startup"""
    await init_category()
    yield


app = FastAPI(
    title="Finora API",
    description="A modern expense tracking platform with comprehensive financial management features",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
    return {"message": "Welcome to Finora API!"}


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
