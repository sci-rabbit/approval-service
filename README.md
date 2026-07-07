# approval-service

Backend-сервис согласования контента: принимает заявки на согласование и фиксирует
итоговое решение (approve / reject / cancel). Внешние сущности (публикации, сценарии,
пользователи, workspace) хранятся только как идентификаторы — соседние сервисы не
реализуются.

Стек: **Python 3.13 · FastAPI · SQLAlchemy (async) · PostgreSQL · Alembic**.

---

## Запуск через Docker (рекомендуется)

```bash
docker compose up --build
```

Поднимается Postgres и приложение. Миграции (`alembic upgrade head`) применяются
автоматически на старте. API доступен на <http://localhost:8000>, интерактивная
документация — <http://localhost:8000/docs>.

Остановить: `docker compose down` (данные сохраняются в томе `pgdata`;
`docker compose down -v` — удалить вместе с данными).

## Локальный запуск (без Docker)

Нужен запущенный PostgreSQL.

```bash
poetry install

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"

alembic upgrade head
uvicorn main:app --reload
```

> Windows PowerShell: `$env:DATABASE_URL = "postgresql+asyncpg://..."`

Если `DATABASE_URL` не задан, используется значение по умолчанию из
[core/config.py](core/config.py).

## Тесты

```bash
poetry install          # ставит dev-группу (pytest, pytest-asyncio, aiosqlite)
pytest
```

Тесты гоняются на in-memory SQLite и поднимают приложение через ASGI — отдельная
БД или запущенный Postgres для них не нужны.

---

## Аутентификация (заглушка)

Реальной авторизации нет: для локального запуска identity передаётся заголовками.
Предполагается, что в проде перед сервисом стоит API-gateway, который проверяет токен
и подставляет эти значения; сервис им доверяет. Замена заглушки на реальную проверку
затрагивает только [core/auth.py](core/auth.py).

| Заголовок          | Обязателен | Пример                                            |
|--------------------|------------|---------------------------------------------------|
| `X-Workspace-Id`   | да         | `ws_1`                                            |
| `X-User-Id`        | да         | `usr_1`                                           |
| `X-Actions`        | да         | `approval:read,approval:create,approval:decide`   |
| `Idempotency-Key`  | только для создания заявки | `demo-1`                          |

`X-Actions` — список разрешённых действий через запятую.

| Действие           | Когда нужно            |
|--------------------|------------------------|
| `approval:read`    | чтение заявок          |
| `approval:create`  | создание заявки        |
| `approval:decide`  | approve / reject       |
| `approval:cancel`  | cancel                 |

Правила доступа:

- нет `X-Workspace-Id` / `X-User-Id` или неизвестное действие в `X-Actions` → **401**;
- у пользователя нет нужного действия, либо workspace в заголовке не совпадает с
  workspace в пути → **403** (так обеспечивается изоляция между workspace);
- `actor_user_id` берётся из `X-User-Id`, а не из тела запроса — подделать автора решения нельзя.

---

## HTTP API

| Метод | Путь | Действие |
|-------|------|----------|
| GET  | `/health` | liveness |
| GET  | `/ready`  | readiness (проверяет БД) |
| POST | `/api/v1/workspaces/{workspace_id}/approval-requests` | создать заявку |
| GET  | `/api/v1/workspaces/{workspace_id}/approval-requests` | список заявок workspace |
| GET  | `/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}` | одна заявка |
| POST | `/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/approve` | согласовать |
| POST | `/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/reject` | отклонить |
| POST | `/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/cancel` | отменить |

Тела решений: approve — `{"comment": "..."}` (необязательно), reject — `{"reason": "..."}`,
cancel — `{"reason": "..."}`.

### Пример

```bash
# создать
curl -X POST http://localhost:8000/api/v1/workspaces/ws_1/approval-requests \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Id: ws_1" -H "X-User-Id: usr_1" \
  -H "X-Actions: approval:create" \
  -H "Idempotency-Key: demo-1" \
  -d '{
        "source_type": "publication",
        "source_id": "pub_123",
        "title": "Instagram reel draft",
        "description": "Needs final approval",
        "reviewer_user_ids": ["usr_1", "usr_2"]
      }'

# согласовать (usr_1 должен быть среди reviewer_user_ids)
curl -X POST http://localhost:8000/api/v1/workspaces/ws_1/approval-requests/<id>/approve \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Id: ws_1" -H "X-User-Id: usr_1" \
  -H "X-Actions: approval:decide" \
  -d '{"comment": "Approved"}'
```

`source_type` ∈ `publication | scenario | edit | external`.

Подробнее о модели данных, границах сервиса, идемпотентности, событиях и известных
компромиссах — в [DESIGN.md](DESIGN.md).
