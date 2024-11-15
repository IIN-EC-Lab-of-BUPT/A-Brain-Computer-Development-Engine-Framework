from abc import ABC, abstractmethod
from typing import Union
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnRegisterComponentCallbackInterface, AddListenerOnUpdateComponentInfoCallbackInterface, \
    AddListenerOnUnregisterComponentCallbackInterface, AddListenerOnUpdateComponentStateCallbackInterface
from componentframework.api.model.MessageModel import ComponentModel


class ComponentManagerInterface(ABC):
    @abstractmethod
    async def component_register(self, component_model: ComponentModel) -> ComponentModel:
        """
        2.6.1 组件注册
        """
        # component_id: 本服务组件ID，默认可为空。如果为空则组件框架注册时自动生成32位UUID，并填入
        # component_type: 本服务组件类型，不可为空。例如用于标识具体某支赛队的算法，多个component_id可以对应同一种component_type。
        # component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
        # 返回component_id
        # 注册component时自动注册同名service，其配置信息与component_info完全相同，具体信息记录操作还是在zookeeper中service节点下进行
        pass

    @abstractmethod
    async def get_component_info(self, component_id: str = None) -> ComponentModel:
        """
        2.6.2 获取指定组件信息
        """
        # 注册中心中，获取指定组件信息
        # 输入参数：
        # - component_id: 指定组件ID，如果为空，则指代本组件自身
        # 返回参数：
        # - GetComponentInfoModel:
        # component_id: 本服务组件ID，默认可为空。如果为空则组件框架注册时自动生成32位UUID，并填入
        # component_type: 本服务组件类型，不可为空。例如用于标识具体某支赛队的算法，多个component_id可以对应同一种component_type。
        # component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
        pass

    @abstractmethod
    async def add_listener_on_register_component(self,
                                                 callback: AddListenerOnRegisterComponentCallbackInterface) -> None:
        """
        2.6.3 组件注册监听回调
        """
        # callback包含输入参数
        # component_id: str, component_type: str, component_info: dict[str, Union[str, dict]]
        # callback无需返回
        pass

    @abstractmethod
    async def update_component_info(self, component_info: dict[str, Union[str, dict]],
                                    component_id: str = None) -> StatusEnum:
        """
        2.6.4 修改组件配置信息
        """
        # 修改component_info: dict，
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # component_info: dict[
        # tr, Union[str, dict]]
        # 更新的组件信息
        # 返回更新成功枚举
        pass

    @abstractmethod
    async def add_listener_on_update_component_info(self, callback: AddListenerOnUpdateComponentInfoCallbackInterface,
                                                    component_id: str = None) -> None:
        """
        2.6.5 监听组件组件配置信息更新回调
        """
        # callback包含输入参数
        # component_id: str, component_info: dict[str, Union[str, dict]]
        # callback
        # 无需返回
        pass

    @abstractmethod
    async def unregister_component(self) -> StatusEnum:
        """
        2.6.6 本组件注销
        """
        # 返回值：注销成功枚举
        pass

    @abstractmethod
    async def add_listener_on_unregister_component(self,
                                                   callback: AddListenerOnUnregisterComponentCallbackInterface) -> None:
        """
        2.6.7 组件注销监听
        """
        # 组件注销监听
        # callback包含输入参数
        # component_id : str, component_type: str, component_info : dict
        # callback 无需返回
        pass

    @abstractmethod
    async def get_all_component(self) -> list[str]:
        """
        2.6.8 获取所有组件信息
        """
        # 返回值：component_id的list列表
        pass

    @abstractmethod
    async def cancel_add_listener_on_register_component(self, component_id: str = None) -> StatusEnum:
        """
        2.6.9 取消组件注册监听回调
        """
        pass

    @abstractmethod
    async def cancel_add_listener_on_update_component_info(self, component_id: str = None) -> StatusEnum:
        """
        2.6.10 取消监听组件组件配置信息更新回调
        """
        pass

    @abstractmethod
    async def cancel_add_listener_on_unregister_component(self, component_id: str = None) -> StatusEnum:
        """
        2.6.11 取消组件注销监听
        """
        pass

    @abstractmethod
    async def update_component_state(self, component_status: ComponentStatusEnum,
                                     component_id: str = None) -> StatusEnum:
        """
        2.6.12 更新组件状态
        """
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # component_status: ComponentStatusEnum
        # 返回值：枚举
        pass

    @abstractmethod
    async def add_listener_on_update_component_state(self, callback: AddListenerOnUpdateComponentStateCallbackInterface,
                                                     component_id: str = None) -> None:
        """
        2.6.12 监听组件状态更新
        """
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # callback包含输入参数
        # component_id : str, component_status: ComponentStatusEnum
        # callback 无需返回
        pass

    @abstractmethod
    async def get_component_state(self, component_id: str = None) -> ComponentStatusEnum:
        """
        2.6.12 获取组件状态
        """
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # 返回值：ComponentStatusEnum枚举
        pass

    @abstractmethod
    async def cancel_add_listener_on_update_component_state(self, component_id: str = None) -> StatusEnum:
        """
        2.6.12 取消组件状态更新监听
        """
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        pass

    @abstractmethod
    async def startup(self, component_startup_configuration):
        pass
