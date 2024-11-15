from Collector.api.exception.CollectorException import CollectorException


class ReceiverException(CollectorException):
    pass


class ReceiverConnectionException(ReceiverException):
    pass
