from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.routes.auth import router as auth_router
from apps.api.routes.auctions import router as auctions_router
from apps.api.routes.bid_requests import router as bid_requests_router
from apps.api.routes.campaigns import router as campaigns_router
from apps.api.routes.events import router as events_router
from apps.api.routes.health import router as health_router
from apps.api.routes.placements import router as placements_router
from apps.api.routes.publishers import router as publishers_router
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
app.include_router(bid_requests_router, prefix="/bid-requests", tags=["bid-requests"])
app.include_router(auctions_router, prefix="/auctions", tags=["auctions"])
app.include_router(events_router, prefix="/events", tags=["events"])
app.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
app.include_router(publishers_router, prefix="/publishers", tags=["publishers"])
app.include_router(placements_router, prefix="/placements", tags=["placements"])
