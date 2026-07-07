import enum


class AuthAction(str, enum.Enum):
    read = "approval:read"
    create = "approval:create"
    decide = "approval:decide"
    cancel = "approval:cancel"
