from ProcessHub.api.exception.ProcessHubException import ProcessHubException


class ProcessHubAlgorithmConnectorException(ProcessHubException):
    pass


class ProcessHubAlgorithmConnectorClosedException(ProcessHubAlgorithmConnectorException):
    pass


class ProcessHubAlgorithmConnectorTimeoutException(ProcessHubAlgorithmConnectorException):
    pass
