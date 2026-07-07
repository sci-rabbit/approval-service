import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import main
from core.database import get_ro_session, get_rw_session
from models.base import Base


from models import ( 
    approval_event,
    approval_request,
    approval_reviewer,
    idempotency_key,
    outbox_event,
)


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory

    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):

    async def override_rw():
        async with session_factory() as session:
            async with session.begin():
                yield session

    async def override_ro():
        async with session_factory() as session:
            yield session

    main.app.dependency_overrides[get_rw_session] = override_rw
    main.app.dependency_overrides[get_ro_session] = override_ro

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    main.app.dependency_overrides.clear()
