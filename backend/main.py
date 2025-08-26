from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.router import router as auth_router
from backend.user.router import router as user_router
from scalar_fastapi import get_scalar_api_reference

import uvicorn 

app = FastAPI(
    title="Gomoku Game API",
    description="A complete Gomoku game backend API with user authentication and game management",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/scalar")
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Scalar",
    )

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)