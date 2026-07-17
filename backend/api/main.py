import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.portfolio import router as portfolio_router


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "")

    default_local_origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
    ]

    configured_origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    return default_local_origins + configured_origins


app = FastAPI(
    title="Portfolio Optimizer API",
    description="Backend API for portfolio analysis and optimization.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router)


@app.get("/")
def root():
    return {"message": "portfolio optimizer api is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}