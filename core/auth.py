from fastapi import Depends, Header, Path

from dto.auth_context_dto import AuthContextDto
from enums.auth_action_enum import AuthAction
from exceptions.auth_exc import Forbidden, Unauthorized


async def get_auth_context(
    x_workspace_id: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
    x_actions: str = Header(default=""),
) -> AuthContextDto:
    if not x_workspace_id or not x_user_id:
        raise Unauthorized()

    actions = set()
    for raw in x_actions.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            actions.add(AuthAction(raw))
        except ValueError:
            raise Unauthorized()

    return AuthContextDto(
        workspace_id=x_workspace_id,
        user_id=x_user_id,
        actions=frozenset(actions),
    )


def require(action: AuthAction):
    
    async def dependency(
        workspace_id: str = Path(...),
        auth: AuthContextDto = Depends(get_auth_context),
    ) -> AuthContextDto:
        if auth.workspace_id != workspace_id:
            raise Forbidden()
        if action not in auth.actions:
            raise Forbidden()
        return auth

    return dependency
