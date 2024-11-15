from enum import Enum


class VirtualReceiverMessageKeyEnum(Enum):
    """
    定义本系统发送/接收消息所需message_key
    枚举对象为系统所引对象，枚举值为message_key，枚举值对应于配置文件中的message字段中的key
    """
    VIRTUAL_RECEIVER_CUSTOM_CONTROL = "virtual_receiver_custom_control"

