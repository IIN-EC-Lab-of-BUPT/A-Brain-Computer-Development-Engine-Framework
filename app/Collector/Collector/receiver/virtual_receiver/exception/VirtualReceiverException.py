from Collector.receiver.exception.ReceiverException import ReceiverException


class VirtualReceiverException(ReceiverException):
    pass


class VirtualReceiverFileNotFoundException(VirtualReceiverException):
    pass
