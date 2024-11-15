from Collector.api.exception.CollectorException import CollectorException


class BusinessCollectorException(CollectorException):
    pass


class BusinessStatusesNotSuitableException(BusinessCollectorException):
    pass
