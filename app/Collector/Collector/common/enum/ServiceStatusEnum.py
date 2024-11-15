from enum import Enum


class ServiceStatusEnum(Enum):
    """
    服务状态定义
    允许状态变化
    INITIALIZING -> READY/ERROR
    READY -> STARTING/STOPPED
    STARTING -> RUNNING/ERROR
    RUNNING -> STOPPING/ERROR
    STOPPING -> READY/STOPPED/ERROR
    STOPPED -> INITIALIZING （服务创建初始状态）
    ERROR -> INITIALIZING/STARTING
    """

    INITIALIZING = 0    # 初始化过程状态
    READY = 1   # 就绪状态
    STARTING = 2    # 启动过程状态
    RUNNING = 3  # 运行状态
    STOPPING = 4    # 停止过程状态
    STOPPED = 5     # 停止状态
    ERROR = 6       # 错误状态


