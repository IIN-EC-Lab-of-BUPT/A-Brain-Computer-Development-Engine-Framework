import asyncio
import contextlib
import logging
from asyncio import Queue, Task, Event

from grpc import RpcError
from grpc._cython.cygrpc import UsageError
from injector import inject

from Task.common.utils.EventManager import EventManager
from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.proto.AlgorithmRPCService_pb2 import AlgorithmDataMessage as AlgorithmDataMessage_pb2
from Task.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Task.common.enum.TaskEventEnum import TaskEventEnum
from Task.facade.excepiton.TaskRPCException import TaskRPCClientClosedException
from Task.facade.interface.ReceiveAlgorithmReportMessageOperatorInterface import \
    ReceiveAlgorithmReportMessageOperatorInterface
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCDataConnectStub


class AlgorithmRPCDataConnectClient:
    @inject
    def __init__(self, event_manager: EventManager):
        self.__event_manager: EventManager = event_manager
        self.__receive_report_operator: ReceiveAlgorithmReportMessageOperatorInterface = None
        self.__data_message_queue: Queue[AlgorithmDataMessage_pb2] = Queue()
        self.__algorithm_rpc_data_connect_stub: AlgorithmRPCDataConnectStub = None
        self.__send_end_flag = True
        self.__receiver_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED
        self.__sender_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED
        self.__disconnect_event = Event()
        self.__logger = logging.getLogger("taskLogger")
        self.__receive_report_task: Task = None
        self.__disconnect_task: Task = None
        self.__algorithm_rpc_message_converter: AlgorithmRPCMessageConverter = AlgorithmRPCMessageConverter()

    async def connect(self):
        self.__logger.info("发起数据连接")
        # 执行算法启动流程
        self.__send_end_flag = False
        self.__receiver_status = ServiceStatusEnum.STARTING
        self.__sender_status = ServiceStatusEnum.STARTING

        async def connect_request_generator():
            self.__sender_status = ServiceStatusEnum.RUNNING
            try:
                while True:
                    message = await self.__data_message_queue.get()  # 使用异步get方法获取待发送消息
                    if self.__send_end_flag and self.__data_message_queue.qsize() == 0:
                        # 如果停止标志为真，且数据发送队列剩余元素为0则结束生成器，最后一个结束包不发送
                        self.__disconnect_event.set()
                        self.__sender_status = ServiceStatusEnum.STOPPED
                        self.__logger.info("数据发送连接已断开")
                        return
                    self.__logger.debug(f"send data {message.sourceLabel}-{type(message).__name__}-{message.WhichOneof('package')}")
                    yield message
                    self.__data_message_queue.task_done()  # 通知队列该任务已完成
            except asyncio.CancelledError:  # 如果流被取消，则正常退出
                self.__logger.info("数据发送任务被取消")
                self.__sender_status = ServiceStatusEnum.STOPPED
                return
            except Exception as e:
                self.__logger.exception(f"数据接收连接异常：{e}")
                raise e

        report_iterator = self.__algorithm_rpc_data_connect_stub.connect(connect_request_generator())
        # 加一个报告接收协程任务
        self.__receive_report_task = asyncio.create_task(self.__receive_report_function(report_iterator))
        self.__logger.info("启动结果接收任务")

    async def disconnect(self):
        # 先判断发送器状态，如果为运行状态，则发送停止信号
        if self.__sender_status == ServiceStatusEnum.RUNNING:
            await self.__stop_sender_process()

        # 再判断接收器状态，如果为运行状态，则发送停止信号
        if self.__receiver_status == ServiceStatusEnum.RUNNING:
            await self.__stop_receiver_process()

    def add_receive_report_operator(self, receive_report_operator: ReceiveAlgorithmReportMessageOperatorInterface):
        self.__receive_report_operator = receive_report_operator

    async def send_data(self, algorithm_data_message: AlgorithmDataMessage_pb2):
        if self.__send_end_flag:
            raise TaskRPCClientClosedException("发送数据时，连接已关闭")
        else:
            await self.__data_message_queue.put(algorithm_data_message)
            self.__logger.debug(f"{algorithm_data_message.sourceLabel}"
                                f"数据写入发送队列:{algorithm_data_message.WhichOneof('package')}")

    async def __receive_report_function(self, request_iterator):
        self.__receiver_status = ServiceStatusEnum.RUNNING
        try:
            async for algorithm_report_message in request_iterator:
                await self.__receive_report_operator.receive_report(
                    self.__algorithm_rpc_message_converter.protobuf_to_model(algorithm_report_message)
                )
        except asyncio.CancelledError:
            self.__logger.info("结果接收任务取消")
        except UsageError:
            self.__logger.info(f"赛题端结果接收流已经关闭")
        except RpcError as rpc_error: # 如果接收器出现异常，则关闭接收器
            self.__logger.exception(f"数据结果接收出现异常，关闭接收器{rpc_error}")
        except Exception as e:
            self.__logger.exception(f"数据结果接收连接异常：{e}")
            raise e
        finally:
            self.__receiver_status = ServiceStatusEnum.STOPPED
            self.__logger.info(
                f"接收结果报告连接结束，发送结束信号事件{TaskEventEnum.ALGORITHM_DISCONNECT.value}")
            # 结束后，发送连接停止事件通知
            asyncio.create_task(self.__event_manager.notify(TaskEventEnum.ALGORITHM_DISCONNECT.value))

    def set_algorithm_rpc_data_connect_stub(self, algorithm_rpc_data_connect_stub: AlgorithmRPCDataConnectStub):
        self.__algorithm_rpc_data_connect_stub = algorithm_rpc_data_connect_stub

    async def __stop_sender_process(self):
        if self.__sender_status is not ServiceStatusEnum.RUNNING:
            return
        self.__sender_status = ServiceStatusEnum.STOPPING
        self.__logger.info("开始断开发送数据连接")
        # 置为结束标志位，并且额外生成一个数据包以触发结束操作
        self.__send_end_flag = True
        stop_response = AlgorithmDataMessage_pb2()
        self.__disconnect_event.clear()
        await self.__data_message_queue.put(stop_response)
        # 阻塞直到数据发送队列把最后一个包发送出去
        await self.__disconnect_event.wait()

    async def __stop_receiver_process(self):
        if self.__receiver_status is not ServiceStatusEnum.RUNNING:
            return
        self.__sender_status = ServiceStatusEnum.STOPPING
        # 等待接收数据任务或超时任务完成，先等待接收数据任务
        if not self.__receive_report_task.done():
            # 创建一个未来的事件，等待20秒，如果20秒内数据接收停止，则正常退出，反之则强制取消数据接收任务
            timeout_task = asyncio.create_task(asyncio.sleep(20))
            done, pending = await asyncio.wait({self.__receive_report_task, timeout_task},
                                               return_when=asyncio.FIRST_COMPLETED)
            # 如果接收数据任务已经完成，就不再执行其他操作
            if self.__receive_report_task in done:
                self.__logger.info("数据接收任务已正常结束")
            else:
                # 如果超时任务先完成，说明接收数据任务需要被取消
                self.__logger.warning("数据接收任务超时，取消任务")
                self.__receive_report_task.cancel()
                # 等待接收数据任务被取消
                with contextlib.suppress(asyncio.CancelledError):
                    await self.__receive_report_task
            # 清理
            for task in pending:
                task.cancel()
        self.__receive_report_task = None
