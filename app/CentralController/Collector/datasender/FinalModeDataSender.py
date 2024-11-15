from typing import Union

import numpy

from Collector.api.message.MessageKeyEnum import MessageKeyEnum
from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Collector.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Collector.datasender.interface.DataSenderInterface import DataSenderInterface
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import DataMessageModel, DataPackageModel, EventPackageModel, DevicePackageModel, \
    ImpedancePackageModel, InformationPackageModel


class FinalModeDataSender(DataSenderInterface):

    def __init__(self):
        super().__init__()
        self.__cached_external_trigger_list: list[ExternalTriggerModel] = list[ExternalTriggerModel]()
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def start_data_sending(self):
        self.__service_status = ServiceStatusEnum.RUNNING

    async def stop_data_sending(self):
        # 清理缓存内容
        self.__cached_external_trigger_list.clear()
        self.__service_status = ServiceStatusEnum.STOPPED

    async def send_data(self, data_message_model: DataMessageModel) -> None:

        # 如果不属于预定义的类型则不发送
        if not isinstance(data_message_model.package,
                          Union[
                              DevicePackageModel,
                              EventPackageModel,
                              DataPackageModel,
                              ImpedancePackageModel,
                              InformationPackageModel,
                          ]):
            return
        # 如果不是运行状态则不发送事件类型数据包合数据类型数据包
        if isinstance(data_message_model.package, Union[EventPackageModel, DataPackageModel]) \
                and self.__service_status != ServiceStatusEnum.RUNNING:
            return

        # 检查是否有缓存的external_trigger，如果有，则打包该trigger，并按照list顺序以当前数据data_position的位置依次+1并发送
        # 如果包内数据对应位置已有trigger，则会在算法端覆盖
        match data_message_model.package:
            case DataPackageModel():
                await self.__data_package_func(data_message_model)
            case _:
                await self.__default_func(data_message_model)

    async def receiver_external_trigger(self, external_trigger_model: ExternalTriggerModel) -> None:
        # 如果不是运行状态则不记录
        if self.__service_status != ServiceStatusEnum.RUNNING:
            return

        # 收到外部trigger，缓存入list，待下一次数据发送时发出
        self.__cached_external_trigger_list.append(external_trigger_model)

    async def __data_package_func(self, data_message_model: DataMessageModel):
        data_package_model: DataPackageModel = data_message_model.package
        # 判断数据类型并转换
        if isinstance(data_package_model.data, list):
            if len(data_package_model.data) > 0:
                first_data = data_package_model.data[0]
                if isinstance(first_data, float):
                    data_package_model.data = numpy.ndarray(data_package_model.data, dtype=numpy.float32)
                elif isinstance(first_data, int):
                    data_package_model.data = numpy.ndarray(data_package_model.data, dtype=numpy.int32)
        elif isinstance(data_package_model.data, numpy.ndarray):
            if data_package_model.data.dtype == numpy.float64:
                data_package_model.data = data_package_model.data.astype(numpy.float32)
            elif data_package_model.data.dtype == numpy.int64:
                data_package_model.data = data_package_model.data.astype(numpy.int32)

        this_data_position = data_package_model.data_position

        for external_trigger_index, external_trigger in enumerate(self.__cached_external_trigger_list):
            event_package_model = EventPackageModel(
                event_position=[this_data_position + external_trigger_index],
                event_data=[external_trigger.trigger]
            )
            await self._component_framework.send_message(
                MessageKeyEnum.SEND_DATA.value,
                CommonMessageConverter.model_to_protobuf(event_package_model).SerializeToString()
            )
        # 清理缓存
        self.__cached_external_trigger_list.clear()
        await self._component_framework.send_message(
            MessageKeyEnum.SEND_DATA.value,
            CommonMessageConverter.model_to_protobuf(data_message_model).SerializeToString()
        )

    async def __default_func(self, data_message_model: DataMessageModel):
        await self._component_framework.send_message(
            MessageKeyEnum.SEND_DATA.value,
            CommonMessageConverter.model_to_protobuf(data_message_model).SerializeToString()
        )
