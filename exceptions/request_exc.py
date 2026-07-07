from exceptions.base import BaseAppException


class RequestNotFound(BaseAppException):
    status_code = 404
    detail = "Request not found"

class RequestAlreadyFinalized(BaseAppException):
    status_code = 409
    detail = "Request already finalized"

class PermissionDenied(BaseAppException):
    status_code = 403
    detail = "Permission denied"