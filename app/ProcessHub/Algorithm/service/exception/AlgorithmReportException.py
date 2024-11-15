from Algorithm.api.exception.AlgorithmException import AlgorithmException


class AlgorithmReportException(AlgorithmException):
    pass


class AlgorithmReportResultTypeIsNotSupportedException(AlgorithmReportException):
    def __init__(self, result_type: str):
        super().__init__(f"The result type '{result_type}' is not supported. Only None, bool, str, bytes, list[float], "
                         f"list[int], list[str] are supported")
