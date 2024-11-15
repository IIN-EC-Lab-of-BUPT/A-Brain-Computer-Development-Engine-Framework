from enum import Enum


class ComponentStatusEnum(Enum):
    STOP = 'STOP'  # 表示操作或任务执行成功完成
    RUNNING = 'RUNNING'  # 表示操作或任务执行失败
    ERROR = 'ERROR'  # 表示操作或任务处于等待执行的状态
