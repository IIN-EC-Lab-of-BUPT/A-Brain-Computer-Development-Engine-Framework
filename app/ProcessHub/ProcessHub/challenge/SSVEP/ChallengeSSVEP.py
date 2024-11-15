import os
import random
from typing import Union

import yaml

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from Common.model.CommonMessageModel import ScorePackageModel, ResultPackageModel, ControlPackageModel
from ProcessHub.challenge.interface.ChallengeInterface import ChallengeInterface
from ProcessHub.orchestrator.model.SourceModel import SourceModel


class ChallengeSSVEP(ChallengeInterface):

    def __init__(self):
        super().__init__()
        self.__source_list: list[SourceModel] = list()
        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__current_trial_id = 0
        self.__current_result_model: ResultPackageModel = None

    async def initial(self):
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        challenge_config_file_name = 'ChallengeSSVEP.yml'
        challenge_config_path = os.path.join(directory_path, challenge_config_file_name)
        with open(challenge_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)
        # # 加载source配置信息
        source_dict = self.__config_dict.get('sources', dict[str, dict[str, str]]())
        for source_label, source_topic in source_dict.items():
            self.__source_list.append(SourceModel(source_label, source_topic))

    async def startup(self):
        # 启动时执行的逻辑
        pass

    async def shutdown(self):
        # 关闭时执行的逻辑
        pass

    async def update(self, config_dict: dict[str, Union[str, dict]]):
        pass

    async def get_to_algorithm_config(self) -> dict[str, Union[str, dict]]:
        return self.__config_dict.get('challenge_to_algorithm_config', dict[str, Union[str, dict]]())

    async def get_source_list(self) -> list[SourceModel]:
        return self.__source_list

    async def get_to_strategy_config(self) -> dict[str, Union[str, dict]]:
        return self.__config_dict.get('strategy_config', dict[str, Union[str, dict]]())

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) \
            -> Union[AlgorithmDataMessageModel, None]:
        # 需要针对algorithm_data_message_model中不同来源，不同类型的数据包(DevicePackageModel,EventPackageModel
        # DataPackageModel,ImpedancePackageModel，InformationPackageModel，ControlpackageModel)进行预处理
        return algorithm_data_message_model

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel) -> None:
        if isinstance(algorithm_report_message_model.package, ResultPackageModel):
            # 只需要处理ResultPackageModel类型数据包即可
            result_package_model: ResultPackageModel = algorithm_report_message_model.package
            self.__current_result_model = result_package_model
            # result_package_model中数据类型会被自动转换成发送时对应的数据类型
            result_data = result_package_model.result
            report_source_information = result_package_model.report_source_information
            source_position_position_list = [source_info.position for source_info in report_source_information]
        elif isinstance(algorithm_report_message_model.package, ControlPackageModel):
            # 需要处理ControlpackageModel类型数据包
            control_package_model: ControlPackageModel = algorithm_report_message_model.package
            end_flag = control_package_model.end_flag
        # 不需要返回值

    async def timeout_trigger(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        # 超时触发逻辑
        pass

    async def get_score(self) -> list[ScorePackageModel]:
        # 返回当前block成绩
        return [ScorePackageModel(show_text="test", score=random.random(), trial_time=random.random(),
                                  trial_id=str(self.__current_trial_id), block_id='0', subject_id='0')]



