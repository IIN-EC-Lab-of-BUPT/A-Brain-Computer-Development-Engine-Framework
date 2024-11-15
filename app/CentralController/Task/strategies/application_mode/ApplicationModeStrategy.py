from typing import Union

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from Task.strategies.interface.StrategyInterface import StrategyInterface


# @singleton
# 单例模式
class ApplicationModeStrategy(StrategyInterface):
    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) -> Union[
        AlgorithmDataMessageModel, None]:
        pass

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        pass

    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    async def update(self, config_dict: dict[str, dict[str, Union[str, dict]]]) -> None:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
