import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import JSONResponse

from api.v1.routes.health import router as health_router
from api.v1.routes.workspaces import router as workspaces_router
from core.database import dispose
from exceptions.base import BaseAppException

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc: BaseAppException):
    if exc.status_code >= 500:
        logger.error("Unhandled exception on %s: %s", request.url.path, exc.detail, exc_info=exc)
    else:
        logger.warning("Client error %d on %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.include_router(health_router)
app.include_router(workspaces_router, prefix="/api/v1")