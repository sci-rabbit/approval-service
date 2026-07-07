from exceptions.base import BaseAppException


class Unauthorized(BaseAppException):
    status_code = 401
    detail = "Missing or invalid auth context"


class Forbidden(BaseAppException):
    status_code = 403
    detail = "Action not permitted in this workspace"
