from enum import Enum


class StatusEnum(Enum):
    SUCCESS = 'SUCCESS'  # 表示操作或任务执行成功完成
    FAILURE = 'FAILURE'  # 表示操作或任务执行失败
    PENDING = 'PENDING'  # 表示操作或任务处于等待执行的状态
    IN_PROGRESS = 'IN_PROGRESS'  # 表示操作或任务正在进行中
    COMPLETED = 'COMPLETED'  # 表示操作或任务已经完成
    CANCELED = 'CANCELED'  # 表示操作或任务已被取消
    ERROR = 'ERROR'  # 表示操作或任务发生了错误
    NOT_FOUND = 'NOT_FOUND'  # 表示在指定的位置或资源中未找到所需的对象或数据
    UNAUTHORIZED = 'UNAUTHORIZED'  # 表示用户未经授权执行指定操作
    FORBIDDEN = 'FORBIDDEN'  # 表示用户被拒绝执行指定的操作
    BAD_REQUEST = 'BAD_REQUEST'  # 表示请求包含无效或不合法的参数或数据
