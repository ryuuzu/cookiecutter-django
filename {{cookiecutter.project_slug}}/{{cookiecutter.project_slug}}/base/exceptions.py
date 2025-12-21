class BaseException(Exception):
    def __init__(
        self, title: str, detail: str, code: str = "exception", status_code: int = 400
    ):
        """
        Base exception class for custom exceptions.

        :param title: Title of the exception
        :param detail: Detailed message of the exception
        :param code: Error code identifier
        """
        self.title = title
        self.detail = detail
        self.code = code
        self.status_code = status_code

    def __str__(self):
        return f"{self.title}: {self.detail}"


class Unauthorized(BaseException):
    def __init__(
        self,
        detail: str,
        title: str = "Unauthorized",
        code: str = "unauthorized",
    ):
        super().__init__(title=title, detail=detail, code=code, status_code=401)


class BadRequest(BaseException):
    def __init__(
        self, detail: str, title: str = "Bad Request", code: str = "bad_request"
    ):
        super().__init__(title=title, detail=detail, code=code, status_code=400)


class Forbidden(BaseException):
    def __init__(self, detail: str, title: str = "Forbidden", code: str = "forbidden"):
        super().__init__(title=title, detail=detail, code=code, status_code=403)


class NotFound(BaseException):
    def __init__(self, detail: str, title: str = "Not Found", code: str = "not_found"):
        super().__init__(title=title, detail=detail, code=code, status_code=404)
