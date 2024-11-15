import logging
from queue import Queue
from typing import Union, Optional
from injector import inject
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import ResultPackageModel, InformationPackageModel, DataMessageModel, \
    ScorePackageModel
from Stimulator.Paradigm.interface.paradigminterface import ParadigmInterface
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel
from Stimulator.facade.interface.TriggerSystemInterface import TriggerSystemInterface
from Stimulator.service.interface.ServiceManagerInterface import TriggerManagerInterface, \
    BusinessManagerInterface, ParadigmManagerInterface
from Stimulator.test.sendinformation import sendinformation
from Stimulator.ui.ui import choice_start_block


class BusinessManager(BusinessManagerInterface):
    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__send_information_message_topic = None
        self.current_information_model = None
        self.current_information_protobuf = None
        self.current_block_id = None
        self.current_subject_id = None
        self.start_block_id = None
        self.start_subject_id = None
        self.random_number_seeds_model = None
        self.queue = Queue()
        self.current_information = None
        self.__config_dict = None
        self.__paradigm_manager: Optional[ParadigmManagerInterface] = None
        self.__trigger_manager: Optional[TriggerManagerInterface] = None
        self.__component_framework: Optional[ComponentFrameworkInterface] = component_framework

        self.__send_external_trigger_topic: Optional[str] = None
        self.__logger = logging.getLogger("stimulatorLogger")

        self.__current_paradigm: Optional[ParadigmInterface] = None
        self.__current_trigger: Optional[TriggerSystemInterface] = None

    async def choice_start_block(self):
        self.start_subject_id, self.start_block_id = choice_start_block()
        self.current_subject_id = str(self.start_subject_id)
        self.current_block_id = str(self.start_block_id)
        # print(111, )
        self.__logger.debug(f"本次实验的被试者id为{self.current_subject_id}+起始block为{self.current_block_id}")
        component_model = await self.__component_framework.get_component_model()
        business_component_info = component_model.component_info
        business_component_info['subject_id'] = self.start_subject_id
        business_component_info['start_block_id'] = self.start_block_id
        await self.__component_framework.update_component_info(business_component_info,
                                                               component_model.component_id)
        return self.start_block_id

    async def send_information(self):
        self.current_information_model = DataMessageModel(package=
                                                          InformationPackageModel(subject_id=self.current_subject_id,
                                                                                  block_id=self.current_block_id))
        self.__logger.debug(f"发送information package:{self.current_information_model}")
        self.current_information_protobuf = CommonMessageConverter.model_to_protobuf(self.current_information_model)
        self.current_information = self.current_information_protobuf.SerializeToString()
        await self.__component_framework.send_message(MessageKeyEnum.INFORMATION.value, self.current_information)
        self.current_block_id = str(int(self.current_block_id) + 1)
        return

    # async def __send_information(self, current_information: bytes):
    #     await self.__component_framework.send_message(MessageKeyEnum.INFORMATION.value, current_information)

    async def set_random_number_seeds(self, random_number_seeds_model: RandomNumberSeedsModel):
        await self.__current_paradigm.receive_random_number_seeds(random_number_seeds_model)
        # self.__logger.debug(f"收到random_number_seeds_model:{random_number_seeds_model}")

    async def start_stimulation_system(self) -> None:
        await self.__current_paradigm.prepare()
        await self.__current_paradigm.run()

    async def stop_stimulation_system(self):
        await self.__current_paradigm.stop()

    async def set_feedback_control_message(self, FeedbackControlModel: DataMessageModel):
        if type(FeedbackControlModel) is ResultPackageModel:
            await self.__current_paradigm.receive_feedback_message(FeedbackControlModel)
        else:
            pass

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        self.__config_dict = config_dict
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        send_information_message_key = MessageKeyEnum.INFORMATION.value
        self.__send_external_trigger_topic = message_key_topic_dict.get(send_information_message_key, None)
        self.__logger.debug("BusinessManager初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        send_information_message_key = MessageKeyEnum.INFORMATION.value
        self.__send_information_message_topic = message_key_topic_dict.get(send_information_message_key, None)

    async def startup(self) -> None:
        self.__current_paradigm = self.__paradigm_manager.get_paradigm()
        self.__logger.debug("当前paradigm已获取")
        self.__current_trigger = self.__trigger_manager.get_trigger_sender()
        self.__logger.debug("当前trigger send已获取")
        await self.__current_trigger.initial(self.__config_dict)
        await self.__current_paradigm.set_trigger_send(self.__current_trigger)
        await self.__current_paradigm.initial(self.__config_dict)
        await self.__current_paradigm.set_component_framework(self.__component_framework)

        # 绑定所需消息
        await self.__component_framework.bind_message(MessageBindingModel(message_key=MessageKeyEnum.INFORMATION.value,
                                                                          topic=self.__send_information_message_topic))
        self.__logger.debug("BusinessManager启动完成")

    async def shutdown(self) -> None:
        # 停止指定预处理和指定接收器
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.INFORMATION.value)
        await self.__current_paradigm.close()
        await self.__current_trigger.shutdown()
        self.__logger.debug("BusinessManager关闭完成")

    def set_paradigm_manager(self, paradigm_manager: ParadigmManagerInterface):
        self.__paradigm_manager = paradigm_manager

    def set_trigger_manager(self, trigger_manager: TriggerManagerInterface):
        self.__trigger_manager = trigger_manager
