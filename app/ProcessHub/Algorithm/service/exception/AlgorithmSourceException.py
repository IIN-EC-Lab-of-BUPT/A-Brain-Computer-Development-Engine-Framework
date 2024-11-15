from Algorithm.api.exception.AlgorithmException import AlgorithmException


class AlgorithmSourceException(AlgorithmException):
    pass


class AlgorithmSourceReceiverNotFoundException(AlgorithmSourceException):
    pass


class AlgorithmSourceReceiverIsTurnedOffException(AlgorithmSourceException):
    pass


