from json import loads
from ..models.response import ErrorMessage


class ScreenshotApiError(Exception):
    def __init__(self, message):
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def __str__(self):
        return str(self.__dict__)


class ParameterError(ScreenshotApiError):
    pass


class EmptyApiKeyError(ScreenshotApiError):
    pass


class ResponseError(ScreenshotApiError):
    def __init__(self, message):
        self.message = message
        self.parsed_message = None
        try:
            parsed = loads(message)
            self.parsed_message = ErrorMessage(parsed)
        except Exception:
            pass

    @property
    def parsed_message(self):
        return self._parsed_message

    @parsed_message.setter
    def parsed_message(self, pm):
        self._parsed_message = pm


class ApiAuthError(ResponseError):
    pass


class BadRequestError(ResponseError):
    pass


class FileError(ScreenshotApiError):
    pass


class HttpApiError(ScreenshotApiError):
    pass
