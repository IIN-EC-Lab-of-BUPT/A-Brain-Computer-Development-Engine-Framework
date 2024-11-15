import asyncio
import contextlib
import logging
from asyncio import Queue, Event, Task
from grpc._cython.cygrpc import UsageError
from injector import inject

from Algorithm.common.enum.AlgorithmEventEnum import AlgorithmEventEnum
from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.common.utils.EventManager import EventManager
from Algorithm.control.exception.AlgorithmRPCServiceException import AlgorithmRPCServerClosedException
from Algorithm.control.operator import ReceiveDataOperator
from Algorithm.service.interface.ServiceManagerInterface import CoreControllerInterface

from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCDataConnectServicer
from Algorithm.api.proto.AlgorithmRPCService_pb2 import AlgorithmReportMessage as AlgorithmReportMessage_pb2


class AlgorithmRPCDataConnectServer(AlgorithmRPCDataConnectServicer):

    @inject
    def __init__(self, core_controller: CoreControllerInterface, event_manager: EventManager):
        self.__core_controller: CoreControllerInterface = core_controller
        self.__event_manager: EventManager = event_manager
        self.__receive_data_operator: ReceiveDataOperator = None
        self.__report_message_queue: Queue[AlgorithmReportMessage_pb2] = Queue()
        self.__send_end_flag = True
        self.__receiver_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED
        self.__sender_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED
        self.__disconnect_event = Event()
        self.__logger = logging.getLogger("algorithmLogger")
        self.__receive_data_task: Task = None
        self.__disconnect_task: Task = None

    async def connect(self, request_iterator, context):
        self.__logger.info("接收到数据连接，抛出数据连接事件")
        # 执行算法启动流程
        await self.__event_manager.notify(AlgorithmEventEnum.RPC_DATA_INPUT_CONNECT_STARTED.value)
        self.__send_end_flag = False
        self.__receiver_status = ServiceStatusEnum.STARTING
        self.__sender_status = ServiceStatusEnum.STARTING
        try:
            self.__receive_data_task = asyncio.create_task(self.__receive_data_function(request_iterator))
            self.__logger.info("启动数据接收任务")
            self.__sender_status = ServiceStatusEnum.RUNNING
            while True:
                message = await self.__report_message_queue.get()  # 使用异步get方法获取待发送消息
                if self.__send_end_flag and self.__report_message_queue.qsize() == 0:
                    # 如果停止标志为真，且数据发送队列剩余元素为0则结束生成器，最后一个结束包不发送
                    self.__disconnect_event.set()
                    self.__sender_status = ServiceStatusEnum.STOPPED
                    self.__logger.info("数据发送连接已断开")
                    return
                self.__logger.debug(f"send data {message.__class__.__name__}-{message.WhichOneof('package')}")
                yield message
                self.__report_message_queue.task_done()  # 通知队列该任务已完成
        except asyncio.CancelledError:  # 如果流被取消，则正常退出
            self.__logger.info("收到数据连接取消异常，尝试关闭连接")
            self.__sender_status = ServiceStatusEnum.STOPPED
            await self.disconnect()  # 启动连接关闭流程，确保输入连接关闭流程正常执行
        except Exception as e:
            self.__logger.exception(f"数据发送连接异常：{e}")
            raise e

    async def disconnect(self):
        # 先判断发送器状态，如果为运行状态，则发送停止信号
        if self.__sender_status == ServiceStatusEnum.RUNNING:
            await self.__stop_sender_process()

        # 再判断接收器状态，如果为运行状态，则发送停止信号
        if self.__receiver_status == ServiceStatusEnum.RUNNING:
            await self.__stop_receiver_process()

    def add_receive_data_operator(self, receive_data_operator: ReceiveDataOperator):
        self.__receive_data_operator = receive_data_operator

    async def send_report(self, algorithm_report_message: AlgorithmReportMessage_pb2):
        if self.__send_end_flag:
            raise AlgorithmRPCServerClosedException("generate_report called after grpc server disconnect")
        else:
            await self.__report_message_queue.put(algorithm_report_message)
            self.__logger.debug(f"report message to __report_message_queue:{algorithm_report_message}")

    async def __receive_data_function(self, request_iterator):
        self.__receiver_status = ServiceStatusEnum.RUNNING
        try:
            async for algorithm_data_message in request_iterator:
                await self.__receive_data_operator.receive_message(algorithm_data_message)
        except asyncio.CancelledError:
            self.__logger.info("数据接收任务取消")
        except UsageError as usage_error:
            self.__logger.info(f"赛题端数据接收流已经关闭")
        except Exception as e:
            self.__logger.exception(f"数据接收连接异常：{e}")
            raise e
        finally:
            self.__receiver_status = ServiceStatusEnum.STOPPED
            self.__logger.info(
                f"接收数据连接结束，发送结束信号事件{AlgorithmEventEnum.RPC_DATA_INPUT_CONNECT_FINISHED.value}")
            asyncio.create_task(self.__event_manager.notify(AlgorithmEventEnum.RPC_DATA_INPUT_CONNECT_FINISHED.value))

    async def __stop_sender_process(self):
        if self.__sender_status is not ServiceStatusEnum.RUNNING:
            return
        self.__sender_status = ServiceStatusEnum.STOPPING
        self.__logger.info("开始断开发送数据连接")
        # 置为结束标志位，并且额外生成一个数据包以触发结束操作
        self.__send_end_flag = True
        stop_response = AlgorithmReportMessage_pb2()
        self.__disconnect_event.clear()
        await self.__report_message_queue.put(stop_response)
        # 阻塞直到数据发送队列把最后一个包发送出去
        await self.__disconnect_event.wait()

    async def __stop_receiver_process(self):
        if self.__receiver_status is not ServiceStatusEnum.RUNNING:
            return
        self.__sender_status = ServiceStatusEnum.STOPPING
        # 等待接收数据任务或超时任务完成，先等待接收数据任务
        if not self.__receive_data_task.done():
            # 创建一个未来的事件，等待20秒，如果20秒内数据接收停止，则正常退出，反之则强制取消接收数据任务
            timeout_task = asyncio.create_task(asyncio.sleep(20))
            done, pending = await asyncio.wait({self.__receive_data_task, timeout_task},
                                               return_when=asyncio.FIRST_COMPLETED)
            # 如果接收数据任务已经完成，就不再执行其他操作
            if self.__receive_data_task in done:
                self.__logger.info("数据接收任务已正常结束")
            else:
                # 如果超时任务先完成，说明接收数据任务需要被取消
                self.__logger.warning("数据接收任务超时，取消任务")
                self.__receive_data_task.cancel()
                # 等待接收数据任务被取消
                with contextlib.suppress(asyncio.CancelledError):
                    await self.__receive_data_task
            # 清理
            for task in pending:
                task.cancel()
            self.__receive_data_task = None
