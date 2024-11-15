from Common.exception.BciCompetitionFrameworkException import BciCompetitionFrameworkException


class CollectorException(BciCompetitionFrameworkException):
    pass


class ReceiverNotSupportCommandException(CollectorException):
    pass
