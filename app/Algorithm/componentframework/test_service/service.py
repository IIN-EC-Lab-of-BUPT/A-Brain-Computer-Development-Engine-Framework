import time
import grpc
import yaml
from future.moves import sys
from test_grpc import ConfigManager_pb2, ConfigManager_pb2_grpc
from test_grpc import ConnectManager_pb2, ConnectManager_pb2_grpc
from test_grpc import MessageManager_pb2, MessageManager_pb2_grpc
from test_grpc import ComponmentManager_pb2, ComponmentManager_pb2_grpc
from concurrent import futures


class ConfigManagerService(ConfigManager_pb2_grpc.ConfigManagerServiceServicer):
    notice = None
    config = None

    def ReadGlobalConfig(self, request, context):
        print(request)
        data = {
            'name': 'John Doe',
            'age': 30,
            'is_employee': True,
            'skills': ['Python', 'YAML']
        }
        # 将字典转换为YAML格式的字符串
        yaml_str = yaml.dump(data)
        response = ConfigManager_pb2.ReadGlobalConfigResponse(response=yaml_str)
        return response

    def ReadUserConfig(self, request, context):
        print(request)
        dict_o = {"ReadUserConfig": "ReadUserConfigSuccessful", "ReadUserConfig1": "ReadUserConfigSuccessful1"}
        response = ConfigManager_pb2.ReadUserConfigResponse(response=dict_o)
        return response

    def RegisterGlobalConfigUpdateCallback(self, request, context):
        print(request)
        for _ in range(2):
            response = ConfigManager_pb2.RegisterGlobalConfigUpdateCallbackResponse(
                callback="RegisterGlobalConfigUpdateCallback")
            yield response
            time.sleep(2)

    def RegisterUserConfigUpdateCallback(self, request, context):
        print(request)
        # if ConfigManagerService.notice:
        #     yield ConfigManagerService.config
        for _ in range(2):
            response = ConfigManager_pb2.RegisterUserConfigUpdateCallbackResponse(
                callback=ConfigManagerService.config)
            yield response
            time.sleep(2)

    def SendPreliminaryConfig(self, request, context):
        print(request)
        if len(request.config) > 0:
            ConfigManagerService.config = request.config
            ConfigManagerService.notice = True
        response = ConfigManager_pb2.SendPreliminaryConfigResponse(response="服务注册成功")
        return response

    def SubScribePreliminaryConfig(self, request, context):
        print(request)
        for _ in range(2):
            response = ConfigManager_pb2.SubScribePreliminaryConfigResponse(
                config=ConfigManagerService.config)
            yield response

    def PullPreliminaryConfig(self, request, context):
        print(request)
        response = ConfigManager_pb2.PullPreliminaryConfigResponse(config=ConfigManagerService.config)
        return response


class MessageManagerService(MessageManager_pb2_grpc.MessageManagerServiceServicer):
    def SubscribeTopic(self, request, context):
        print(request)
        for _ in range(20):
            response = MessageManager_pb2.SubscribeTopicResponse(serviceID='1', messageKey='2', topic='3',
                                                                 changeTypes='4')
            yield response
            time.sleep(1)

    def SendMessage(self, request, context):
        for result in request:
            print(result)
        response = MessageManager_pb2.SendMessageResponse(response="SendMessage Successful")
        return response

    def SendResult(self, request, context):
        # data_msg = CommonMessage_pb2.DataMessage()
        # message = data_msg.ScorePackage  # 假设 'MyMessage' 是你的 protobuf 消息类型
        # message.ParseFromString(request.value)
        print(request.value)
        response = MessageManager_pb2.SendResultResponse(response="SendMessage Successful")
        return response

    def UnsuscribeTopic(self, request, context):
        print(request.request)
        print("取消订阅成功通知")
        response = MessageManager_pb2.UnsuscribeTopicResponse(response="取消订阅成功通知")
        return response


class ComponentManagerService(ComponmentManager_pb2_grpc.ComponentManagerServiceServicer):
    def RegisterComponentStateChangeListener(self, request, context):
        print(request)
        response = ComponmentManager_pb2.RegisterComponentStateChangeListenerResponse(response="start")
        yield response
        time.sleep(20)
        # response = ComponmentManager_pb2.RegisterComponentStateChangeListenerResponse(response="stop")
        # yield response


class ConnectManagerService(ConnectManager_pb2_grpc.ConnectManagerServiceServicer):
    def __init__(self, server):
        self.server = server
        self.running = True

    def ShutDown(self, request, context):
        print("Shutting down gRPC server...")
        self.server.stop(None)  # 设置 grace 参数为 None 表示立即关闭，也可以设置一个时间参数
        print("Server stopped.")
        time.sleep(5)
        self.running = False
        sys.exit()


def serve_main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    ConfigManager_pb2_grpc.add_ConfigManagerServiceServicer_to_server(ConfigManagerService(), server)
    MessageManager_pb2_grpc.add_MessageManagerServiceServicer_to_server(MessageManagerService(), server)
    ComponmentManager_pb2_grpc.add_ComponentManagerServiceServicer_to_server(ComponentManagerService(), server)
    ConnectManager_pb2_grpc.add_ConnectManagerServiceServicer_to_server(ConnectManagerService(server), server)
    server.add_insecure_port('localhost:9000')
    server.start()
    print("Server started. Listening on port 500577...")
    # while ConnectManagerService.running:
    server.wait_for_termination()


if __name__ == '__main__':
    serve_main()
