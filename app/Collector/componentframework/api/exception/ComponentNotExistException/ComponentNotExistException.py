from componentframework.api.exception.ComponentframeworkException import ComponentframeworkException


class ComponentNotExistException(ComponentframeworkException):
    def __init__(self, message: str):
        super().__init__(message)
