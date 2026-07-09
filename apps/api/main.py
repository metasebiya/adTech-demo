from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.routes.auth import router as auth_router
from apps.api.routes.health import router as health_router
from infra.db.init_db import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AdTech Demo API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
