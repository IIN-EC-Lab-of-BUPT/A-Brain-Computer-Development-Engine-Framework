from Task.api.exception.TaskException import TaskException


class TaskRPCException(TaskException):
    pass


class TaskRPCClientClosedException(TaskRPCException):
    pass


class TaskRPCClientTimeoutException(TaskRPCException):
    pass
