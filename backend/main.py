from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from database.database import engine, Base
from routers import auth, groups, monitoring, billing, notifications
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц при запуске
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Плагиат-Детектор API",
    description="API для VK Mini App по поиску плагиата",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])


@app.get("/")
async def root():
    return {"message": "Плагиат-Детектор API работает!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 