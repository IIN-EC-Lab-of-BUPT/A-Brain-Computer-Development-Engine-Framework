import yaml

from CentralController.common.enum.ComponentCategoryEnum import ComponentCategoryEnum
from CentralController.common.model.ComponentInformationModel import ComponentInformationModel
from CentralController.common.model.GroupInformationModel import GroupInformationModel
from Collector.api.message.MessageKeyEnum import MessageKeyEnum as CollectorMessageKeyEnum
from Collector.receiver.virtual_receiver.api.message.VirtualReceiverMessageKeyEnum import VirtualReceiverMessageKeyEnum
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum as StimulatorMessageKeyEnum
from Task.api.message.MessageKeyEnum import MessageKeyEnum as TaskMessageKeyEnum


class CentralControllerConfigCreator:

    def __init__(self):
        self.team_id_list = [
            'team_0',
            'team_1',
            'team_2',
            'team_3',
            'team_4',
            'team_5',
            'team_6',
            'team_7',
            'team_8',
            'team_9',
            'team_10',
        ]
        self.group_id_list = [
            'group_1',
            'group_2',
            'group_3',
        ]
        self.components = list[ComponentInformationModel]()

    def run(self):
        central_controller_config_dict = {}
        groups_dict = dict()
        group_information_model = CentralControllerConfigCreator.create_group_model('group_base')
        groups_dict['group_base'] = self.group_information_model_to_dict(group_information_model)
        for group_id in self.group_id_list:
            group_information_model = CentralControllerConfigCreator.create_group_model(group_id)
            groups_dict.update(self.group_information_model_to_dict(group_information_model))
            # 构建处理组件
            group_processor_component_model_list = list()
            for team_id in self.team_id_list:
                processor_component_model = CentralControllerConfigCreator.create_processor_model(group_id, team_id)
                self.components.append(processor_component_model)
                group_processor_component_model_list.append(processor_component_model)
            # 构建采集组件
            collector_component_model = self.create_collector_model(group_id)
            self.components.append(collector_component_model)
            # 构建刺激组件，依赖对应group的采集组件
            stimulator_component_model = self.create_stimulator_model(
                group_id, group_processor_component_model_list[0].component_id, collector_component_model.component_id)
            self.components.append(stimulator_component_model)

        # 构建其他组件

        data_storage_model = self.create_data_storage_model(self.group_id_list)
        self.components.append(data_storage_model)
        database_model = self.create_database_model(self.group_id_list, self.team_id_list)
        self.components.append(database_model)
        central_controller_component_model = self.create_central_controller_model()
        self.components.append(central_controller_component_model)

        central_controller_config_dict['groups'] = groups_dict
        central_controller_config_dict['components'] = dict()
        for component in self.components:
            central_controller_config_dict['components'].update(
                self.component_information_model_to_dict(component)
            )

        with open('CentralControllerConfig.yml', 'w', encoding='utf-8') as file:
            yaml.dump(central_controller_config_dict, file, sort_keys=False)

    @staticmethod
    def create_group_model(group_id: str) -> GroupInformationModel:
        group_information_model = GroupInformationModel()
        group_information_model.group_id = group_id
        group_information_model.group_info = dict()
        group_information_model.message_key_topic_dict = dict()
        return group_information_model

    def create_stimulator_model(self, group_id: str,
                                feed_back_component_id: str = None,
                                virtual_receiver_component_id: str = None) -> ComponentInformationModel:
        feedback_control_topic = next((component.message_key_topic_dict.get(TaskMessageKeyEnum.REPORT.value)
                                       for component in self.components
                                       if component.component_id == feed_back_component_id), None)

        virtual_receiver_custom_control = next((component.message_key_topic_dict.get(
            VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value)
                                       for component in self.components
                                       if component.component_id == virtual_receiver_component_id), None)

        component_information_model = ComponentInformationModel()
        component_information_model.component_id = 'stimulator_' + group_id
        component_information_model.component_type = ComponentCategoryEnum.STIMULATOR.value
        component_information_model.component_info = {
            'external_trigger_address': '127.0.0.1:8972',
        }
        component_information_model.component_group_id = group_id
        component_information_model.message_key_topic_dict = {
            'command_control': f"{component_information_model.component_id}.command_control",
            'feedback_control': f"{feedback_control_topic}",
            'information': f"{group_id}.data",
            'random_number_seeds': f"{component_information_model.component_id}.random_number_seeds",
            'virtual_receiver_custom_control': f"{virtual_receiver_custom_control}",
        }
        return component_information_model

    @staticmethod
    def create_collector_model(group_id: str) -> ComponentInformationModel:
        component_information_model = ComponentInformationModel()
        component_information_model.component_id = 'collector_' + group_id
        component_information_model.component_type = ComponentCategoryEnum.COLLECTOR.value
        component_information_model.component_info = dict()
        component_information_model.component_group_id = group_id
        component_information_model.message_key_topic_dict = {
            'send_data': f"{group_id}.data",
            'command_control': f"{component_information_model.component_id}.command_control",
            'external_trigger': f"{component_information_model.component_id}.external_trigger",
            'virtual_receiver_custom_control':
                f"{component_information_model.component_id}.virtual_receiver_custom_control",

        }
        return component_information_model

    @staticmethod
    def create_processor_model(group_id: str, team_id: str) -> ComponentInformationModel:
        component_information_model = ComponentInformationModel()
        component_information_model.component_id = team_id + '.' + group_id
        component_information_model.component_type = ComponentCategoryEnum.PROCESSOR.value
        component_information_model.component_info = {
            'algorithm_connection': {
                'address': 'localhost:9981'
            }
        }
        component_information_model.component_group_id = group_id
        component_information_model.message_key_topic_dict = {
            'report': f"{component_information_model.component_id }.report",
            'eeg_1': f"{group_id}.data",
            'command_control': f"{component_information_model.component_id }.command_control",
        }
        return component_information_model

    @staticmethod
    def create_data_storage_model(group_id_list: list[str]) -> ComponentInformationModel:
        component_information_model = ComponentInformationModel()
        component_information_model.component_id = 'data_storage'
        component_information_model.component_type = ComponentCategoryEnum.DATASTORAGE.value
        # 注册时即填入所需要订阅的message_key
        data_storage_message_key_to_topic_dict = {
            f"{group_id}.data": f"{group_id}.data" for group_id in group_id_list
        }

        component_information_model.component_info = {
            "message": {
                message_key: None
                for message_key in
                data_storage_message_key_to_topic_dict.keys()
            },
            "stimulator_components": {
                f"stimulator_{group_id}": None for group_id in group_id_list
            },
        }
        component_information_model.component_group_id = 'group_base'
        component_information_model.message_key_topic_dict = {
            'command_control': f"{component_information_model.component_id}.command_control"
        }
        component_information_model.message_key_topic_dict.update(data_storage_message_key_to_topic_dict)
        return component_information_model

    @staticmethod
    def create_database_model(group_id_list: list[str], team_id_list: list[str]) -> ComponentInformationModel:
        component_information_model = ComponentInformationModel()
        component_information_model.component_id = 'database'
        component_information_model.component_type = ComponentCategoryEnum.DATABASE.value
        # 注册时即填入所需要订阅的message_key
        data_storage_message_key_to_topic_dict = {
            f"{group_id}.data": f"{group_id}.data" for group_id in group_id_list
        }
        result_storage_message_key_to_topic_dict = {
            f"{team_id}.{group_id}.report": f"{team_id}.{group_id}.report"
            for team_id in team_id_list for group_id in group_id_list
        }
        total_storage_message_key_to_topic_dict = dict()
        total_storage_message_key_to_topic_dict.update(data_storage_message_key_to_topic_dict)
        total_storage_message_key_to_topic_dict.update(result_storage_message_key_to_topic_dict)

        component_information_model.component_info = {
            'message': {
                message_key: None
                for message_key in
                data_storage_message_key_to_topic_dict.keys()
            },
            "process_components": {
                f"{team_id}.{group_id}": f"{team_id}.{group_id}.report"
                for team_id in team_id_list for group_id in group_id_list
            },
            "stimulator_components": {
                f"stimulator_{group_id}": None for group_id in group_id_list
            },
        }

        component_information_model.component_group_id = 'group_base'
        component_information_model.message_key_topic_dict = {
            'command_control': f"{component_information_model.component_id}.command_control"
        }
        component_information_model.message_key_topic_dict.update(total_storage_message_key_to_topic_dict)
        return component_information_model

    def create_central_controller_model(self) -> ComponentInformationModel:
        central_controller_model = ComponentInformationModel()
        central_controller_model.component_id = 'central_controller'
        central_controller_model.component_type = ComponentCategoryEnum.CONTROLLER.value
        central_controller_model.component_info = dict()
        central_controller_model.component_group_id = 'group_base'
        central_controller_model.message_key_topic_dict = {}
        component_info_message_dict = dict()
        for component_information_model in self.components:
            if component_information_model.component_type == 'COLLECTOR':
                key_str = f"{component_information_model.component_id}.{CollectorMessageKeyEnum.COMMAND_CONTROL.value}"
                central_controller_model.message_key_topic_dict[key_str] = key_str
                component_info_message_dict[key_str] = None
            elif component_information_model.component_type == 'STIMULATOR':
                key_str = f"{component_information_model.component_id}.{StimulatorMessageKeyEnum.COMMAND_CONTROL.value}"
                central_controller_model.message_key_topic_dict[key_str] = key_str
                component_info_message_dict[key_str] = None
                key_str = f"{component_information_model.component_id}.{StimulatorMessageKeyEnum.RANDOM_NUMBER_SEEDS.value}"
                central_controller_model.message_key_topic_dict[key_str] = key_str
                component_info_message_dict[key_str] = None
            elif component_information_model.component_type == 'DATASTORAGE':
                key_str = f"{component_information_model.component_id}.command_control"
                central_controller_model.message_key_topic_dict[key_str] = key_str
                component_info_message_dict[key_str] = None
            elif component_information_model.component_type == 'DATABASE':
                key_str = f"{component_information_model.component_id}.command_control"
                central_controller_model.message_key_topic_dict[key_str] = key_str
                component_info_message_dict[key_str] = None
        central_controller_model.component_info['message'] = component_info_message_dict
        return central_controller_model

    @staticmethod
    def component_information_model_to_dict(component_information_model: ComponentInformationModel) -> dict:
        return {
            component_information_model.component_id: {
                'component_type': component_information_model.component_type,
                'component_info': component_information_model.component_info,
                'component_group_id': component_information_model.component_group_id,
                'message_key_topic_dict': component_information_model.message_key_topic_dict,
            }
        }

    @staticmethod
    def group_information_model_to_dict(group_information_model: GroupInformationModel) -> dict:
        return {
            group_information_model.group_id:
                {
                    'group_info': group_information_model.group_info,
                    'message_key_topic_dict': group_information_model.message_key_topic_dict,
                }
        }


if __name__ == '__main__':
    CentralControllerConfigCreator().run()
