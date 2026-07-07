from dataclasses import dataclass

from enums.auth_action_enum import AuthAction


@dataclass(frozen=True, slots=True)
class AuthContextDto:
    workspace_id: str
    user_id: str
    actions: frozenset[AuthAction]
