import logging
from collections import namedtuple
from typing import Union

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from Common.model.CommonMessageModel import ControlPackageModel, ResultPackageModel, \
    ExceptionPackageModel, DataMessageModel
from Task.common.enum.TaskEventEnum import TaskEventEnum
from Task.strategies.interface.StrategyInterface import StrategyInterface


# 初赛策略模式
class PreliminaryModeStrategy(StrategyInterface):

    def __init__(self):
        super().__init__()
        # 订阅算法断开事件，以便停止系统
        self.__logger = logging.getLogger("taskLogger")
        self.__TrialMarkTuple = namedtuple("SendTrialModel", ["trial_id", "block_id", "subject_id"])
        self.__send_trial_mark_tuple_set = set[self.__TrialMarkTuple]()

    def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    def update(self, config_dict: dict[str, dict[str, Union[str, dict]]]) -> None:
        pass

    def get_strategy_config(self) -> dict[str, Union[str, dict]]:
        pass

    async def startup(self) -> None:
        self._event_manager.subscribe(TaskEventEnum.ALGORITHM_DISCONNECT.value, self.on_algorithm_disconnect)
        self._event_manager.subscribe(TaskEventEnum.APPLICATION_EXIT.value, self.on_application_exit)

    async def shutdown(self) -> None:
        self._event_manager.unsubscribe(TaskEventEnum.ALGORITHM_DISCONNECT.value, self.on_algorithm_disconnect)
        self._event_manager.unsubscribe(TaskEventEnum.APPLICATION_EXIT.value, self.on_application_exit)

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) \
            -> Union[AlgorithmDataMessageModel, None]:

        return await self._challenge.receive_message(algorithm_data_message_model)

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        if isinstance(algorithm_report_message_model.package, ResultPackageModel):
            await self._challenge.receive_report(algorithm_report_message_model)
            await self._message_forwarder.send_report(
                DataMessageModel(package=algorithm_report_message_model.package)
            )
            score_package_model_list = await self._challenge.get_score()
            for score_package_model in score_package_model_list:
                trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                         block_id=score_package_model.block_id,
                                                         subject_id=score_package_model.subject_id)
                # 如果之前未发送过成绩，则发送成绩，反之不发送
                if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                    await self._message_forwarder.send_report(
                        DataMessageModel(package=score_package_model)
                    )
                    self.__send_trial_mark_tuple_set.add(trial_mark_tuple)

        elif isinstance(algorithm_report_message_model.package, ExceptionPackageModel):
            await self._message_forwarder.send_report(
                DataMessageModel(package=algorithm_report_message_model.package)
            )

    async def on_algorithm_disconnect(self) -> None:
        self.__logger.info("初赛模式收到算法断开连接事件")
        # 往赛题中发送一个结束包
        await self._challenge.receive_report(
            AlgorithmReportMessageModel(package=ControlPackageModel(end_flag=True))
        )
        # 从赛题端再获取一个成绩
        score_package_model_list = await self._challenge.get_score()
        for score_package_model in score_package_model_list:
            trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                     block_id=score_package_model.block_id,
                                                     subject_id=score_package_model.subject_id)
            # 如果之前未发送过成绩，则发送成绩，反之不发送
            if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                await self._message_forwarder.send_report(
                    DataMessageModel(package=score_package_model)
                )
                self.__send_trial_mark_tuple_set.add(trial_mark_tuple)

        # 初赛需要关闭算法系统，决赛并不需要
        await self._core_controller.shutdown_and_close_algorithm_system()

    async def on_application_exit(self) -> None:
        """
        初赛中处理应用退出事件
        :return:
        """
        # 初赛需要关闭连接
        await self._core_controller.shutdown()

