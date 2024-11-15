import asyncio
from typing import Union
import yaml
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnGlobalConfigCallbackInterface, AddListenerOnRegisterComponentCallbackInterface, \
    AddListenerOnUpdateComponentInfoCallbackInterface, AddListenerOnUnregisterComponentCallbackInterface, \
    AddListenerOnBindMessageCallbackInterface, SubscribeTopicCallbackInterface, \
    AddListenerOnRequestComponentStopCallbackInterface
from componentframework.api.impl.ComponentFrameworkManager import ComponentFrameworkManager
from componentframework.api.model.ComponentStartupConfigurationModel import ComponentStartupConfigurationModel
from componentframework.api.model.MessageOperateModel import AddListenerOnRegisterComponentModel


class AddListenerOnGlobalConfigCallback(AddListenerOnGlobalConfigCallbackInterface):
    async def run(self, data: dict[str, Union[str, dict]]) -> None:
        print(data)


class AddListenerOnRegisterComponentCallback(AddListenerOnRegisterComponentCallbackInterface):
    async def run(self, data: AddListenerOnRegisterComponentModel) -> None:
        print(data)


class AddListenerOnUpdateComponentInfoCallback(AddListenerOnUpdateComponentInfoCallbackInterface):
    async def run(self, data) -> None:
        print(data)


class AddListenerOnUnregisterComponentCallback(AddListenerOnUnregisterComponentCallbackInterface):
    async def run(self, data) -> None:
        print(data)


class AddListenerOnBindMessageCallback(AddListenerOnBindMessageCallbackInterface):
    async def run(self, data) -> None:
        print(data)


class SubscribeTopicCallback(SubscribeTopicCallbackInterface):
    async def run(self, data: bytes) -> None:
        print(data)


class AddListenerOnRequestComponentStopCallback(AddListenerOnRequestComponentStopCallbackInterface):
    async def run(self, data: str) -> None:
        print(data)


if __name__ == '__main__':
    async def main():
        """组件框架初始化"""
        app_component_initial = ComponentFrameworkManager()
        app_component_initial.initial()
        component_startup_configuration_model = ComponentStartupConfigurationModel()
        component_startup_configuration_model.server_port = 9000
        component_startup_configuration_model.server_address = "localhost"
        # '10.112.182.127'
        await app_component_initial.startup(component_startup_configuration_model)
        config_manager = app_component_initial.get_config_manager()
        message_manager = app_component_initial.get_message_manager()
        component_manager = app_component_initial.get_component_manager()
        connect_manager = app_component_initial.get_connect_manager()

        with open('test.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        """config test"""
        # await config_manager.get_global_config()
        #
        # result2 = await config_manager.update_global_config(data)
        # print(result2)
        # #
        # add_listener_on_global_config_callback = AddListenerOnGlobalConfigCallback()
        # result3 = await config_manager.add_listener_on_global_config(add_listener_on_global_config_callback)
        """component test"""
        # component_register = await component_manager.component_register(component_type='component_register',
        #                                                                 component_info=data, component_id=None)
        # print(component_register)
        # get_component_info = await component_manager.get_component_info("stim")
        # print(get_component_info)
        # add_listener_on_register_component_callback = AddListenerOnRegisterComponentCallback()
        # await component_manager.add_listener_on_register_component(add_listener_on_register_component_callback)
        # update_component_info = await component_manager.update_component_info(component_info=data,
        #                                                                       component_id="stim")
        # print(update_component_info)
        # add_listener_on_update_component_info_callback = AddListenerOnUpdateComponentInfoCallback()
        # await component_manager.add_listener_on_update_component_info(add_listener_on_update_component_info_callback,
        #                                                               "65156")
        # unregister_component = await component_manager.unregister_component()
        # print(unregister_component)
        # add_listener_on_unregister_component_callback = AddListenerOnUnregisterComponentCallback()
        # await component_manager.add_listener_on_unregister_component(add_listener_on_unregister_component_callback)
        # get_all_component = await component_manager.get_all_component()
        # print(get_all_component)
        """message test"""
        # bind_message = await message_manager.bind_message(message_key="str", component_id="5651", topic="None")
        # print(bind_message)
        # add_listener_on_bind_message_callback = AddListenerOnBindMessageCallback()
        # await message_manager.add_listener_on_bind_message(add_listener_on_bind_message_callback)
        # confirm_bind_message = await message_manager.confirm_bind_message(message_key="412", component_id=None,
        #                                                                   topic="None")
        # print(confirm_bind_message)
        # get_topic_by_message_key = await message_manager.get_topic_by_message_key("5145", "4242")
        # print(get_topic_by_message_key)
        # subscribe_topic_callback = SubscribeTopicCallback()
        # await message_manager.subscribe_topic(subscribe_topic_callback, "3453")
        # for i in range(10):
        #     await message_manager.send_message("5453", b'subscribed')
        # await message_manager.send_unary_message("5453", b'subscribed')
        # unsubscribe_source = await message_manager.unsubscribe_source("654")
        # print(unsubscribe_source)
        """connect test"""
        # add_listener_on_request_component_stop_callback = AddListenerOnRequestComponentStopCallback()
        # await connect_manager.add_listener_on_request_component_stop(add_listener_on_request_component_stop_callback)
        # shutdown = await connect_manager.shutdown()
        # print(shutdown)
        await asyncio.gather(*asyncio.all_tasks())
        # await asyncio.sleep(100)


    asyncio.run(main())
