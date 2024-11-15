from Common.exception.BciCompetitionFrameworkException import BciCompetitionFrameworkException


class AlgorithmException(BciCompetitionFrameworkException):
    def __init__(self, message: str):
        super().__init__(message)
