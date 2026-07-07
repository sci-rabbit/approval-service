ALL_ACTIONS = (
    "approval:read",
    "approval:create",
    "approval:decide",
    "approval:cancel",
)


def auth_headers(
    *,
    workspace_id: str = "ws_1",
    user_id: str = "usr_1",
    actions: tuple[str, ...] = ALL_ACTIONS,
    idempotency_key: str | None = None,
) -> dict[str, str]:
    headers = {
        "X-Workspace-Id": workspace_id,
        "X-User-Id": user_id,
        "X-Actions": ",".join(actions),
    }
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def create_payload(
    *,
    source_type: str = "publication",
    source_id: str = "pub_123",
    title: str = "Instagram reel draft",
    description: str | None = "Needs final approval",
    reviewer_user_ids: list[str] | None = None,
) -> dict:
    return {
        "source_type": source_type,
        "source_id": source_id,
        "title": title,
        "description": description,
        "reviewer_user_ids": reviewer_user_ids or ["usr_1", "usr_2"],
    }
