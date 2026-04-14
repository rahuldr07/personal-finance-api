from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from finance_api.config import get_settings
from finance_api.database import init_db
from finance_api.routers import auth, expenses, reports


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(auth.router)
    app.include_router(expenses.router)
    app.include_router(reports.router)

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
