"""FastAPI app entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from text2sql_app.api.routes import router
from text2sql_app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Text2SQL Analytics Platform", version="0.1.0")
    app.include_router(router)
    return app


app = create_app()