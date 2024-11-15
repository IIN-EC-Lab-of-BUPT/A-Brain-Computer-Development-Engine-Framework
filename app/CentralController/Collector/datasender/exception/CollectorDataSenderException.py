from Collector.api.exception.CollectorException import CollectorException


class CollectorDataSenderException(CollectorException):
    pass


class DataIncompleteException(CollectorDataSenderException):
    pass


class DataDimensionsNotMatchException(DataIncompleteException):
    pass
