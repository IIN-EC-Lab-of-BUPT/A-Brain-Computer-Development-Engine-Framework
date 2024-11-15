from dataclasses import dataclass
from enum import Enum


class ComponentPatternEnum(Enum):
    INDEPENDENCE = 'INDEPENDENCE'  # 表示当前组件为独立模式
    CLUSTER_CENTRAL_CONTROL = 'CLUSTER_CENTRAL_CONTROL'  # 表示当前组件为集群_中控模式
    CLUSTER_NON_CENTRAL_CONTROL = 'CLUSTER_NON_CENTRAL_CONTROL'  # 表示当前组件为集群_非中控模式


@dataclass
# 任务数据类
class ComponentStartupConfigurationModel(object):
    server_address: str = 'localhost'
    server_port: int = 9000
    component_pattern: ComponentPatternEnum = ComponentPatternEnum.INDEPENDENCE
