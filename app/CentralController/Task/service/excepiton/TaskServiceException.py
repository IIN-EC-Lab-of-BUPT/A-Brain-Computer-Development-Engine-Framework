from Task.api.exception.TaskException import TaskException


class TaskServiceException(TaskException):
    pass


class TaskServiceStatusException(TaskServiceException):
    pass
