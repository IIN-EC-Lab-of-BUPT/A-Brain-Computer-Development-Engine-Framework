from Algorithm.api.exception.AlgorithmException import AlgorithmException


class AlgorithmRPCServiceException(AlgorithmException):
    pass


class AlgorithmRPCServerClosedException(AlgorithmRPCServiceException):
    pass
