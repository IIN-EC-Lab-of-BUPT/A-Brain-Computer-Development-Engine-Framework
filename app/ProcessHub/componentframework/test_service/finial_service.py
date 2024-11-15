import grpc
import yaml
from test_grpc import ConfigManager_pb2, ConfigManager_pb2_grpc
from test_grpc import ConnectManager_pb2, ConnectManager_pb2_grpc
from test_grpc import MessageManager_pb2, MessageManager_pb2_grpc
from test_grpc import ComponmentManager_pb2, ComponmentManager_pb2_grpc
from concurrent import futures


# 定义服务端类
class ComponentManagerService(ComponmentManager_pb2_grpc.ComponentManagerServiceServicer):
    def RegisterComponent(self, request, context):
        print(request.componentID)
        return ComponmentManager_pb2.RegisterComponentResponse(callback=request.componentID)

    def GetComponentInfo(self, request, context):
        with open('test.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        yaml_str = yaml.dump(data)
        return ComponmentManager_pb2.GetComponentInfoResponse(componentID='1', componentType='2',
                                                              componentInfo=yaml_str)

    def AddListenerOnRegisterComponent(self, request, context):
        for _ in range(3):
            with open('test.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            yaml_str = yaml.dump(data)

            response = ComponmentManager_pb2.AddListenerOnRegisterComponentResponse(componentId='componentID',
                                                                                    componentType='componentType',
                                                                                    componentInfo=yaml_str)
            yield response

    def UpdateComponentInfo(self, request, context):
        print(request.componentInfo)
        return ComponmentManager_pb2.UpdateComponentInfoResponse(response='Update successful')

    def AddListenerOnUpdateComponentInfo(self, request, context):
        for _ in range(3):
            with open('test.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            yaml_str = yaml.dump(data)
            response = ComponmentManager_pb2.AddListenerOnUpdateComponentInfoResponse(componentID='request',
                                                                                      componentInfo=yaml_str)
            yield response

    def UnregisterComponent(self, request, context):
        return ComponmentManager_pb2.UnregisterComponentResponse(response='SUCCESS')

    def AddListenerOnUnregisterComponent(self, request, context):
        for _ in range(3):
            with open('test.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            yaml_str = yaml.dump(data)
            response = ComponmentManager_pb2.ComponentUnregisteredListenerResponse(componentID='request',
                                                                                   componentType='Component Type',
                                                                                   componentInfo=yaml_str)
            yield response

    def GetAllComponent(self, request, context):
        response = ComponmentManager_pb2.GetAllComponentResponse(componentID=["849", "5546", "564"])
        return response


class ConfigManagerService(ConfigManager_pb2_grpc.ConfigManagerServiceServicer):
    # 2.2.1. 全局配置读取
    def ReadGlobalConfig(self, request, context):
        config = self._read_config_from_storage(request.request)
        return ConfigManager_pb2.ReadGlobalConfigResponse(response=config)

    # 2.2.2. 全局参数配置更新回调注册
    def RegisterGlobalConfigUpdateCallback(self, request, context):
        for _ in range(3):
            print(request.request)
            config = self._read_config_from_storage(request.request)
            response = ConfigManager_pb2.RegisterGlobalConfigUpdateCallbackResponse(callback=config)
            yield response

    # 2.2.3. 手动更新全局配置
    def UpdateGlobalConfig(self, request, context):
        self._update_config_in_storage(request.request)
        return ConfigManager_pb2.UpdateGlobalConfigResponse(response='Configuration updated successfully')

    # 这些方法需要你自己实现，例如从存储中读取、注册回调和更新配置
    def _read_config_from_storage(self, request):
        # 实现从存储中读取配置的逻辑
        with open('test.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        yaml_str = yaml.dump(data, encoding='utf-8')
        return yaml_str

    def _register_callback(self, request):
        # 实现注册回调的逻辑，可能保存到某个列表或数据库中
        pass

    def _update_config_in_storage(self, new_config):
        # 实现更新配置的逻辑
        pass


class ConnectManagerService(ConnectManager_pb2_grpc.ConnectManagerServiceServicer):
    def __init__(self):
        # self.server = server
        self.running = True

    def ShutDown(self, request, context):
        print("Shutting down gRPC server...")
        # self.server.stop(None)  # 设置 grace 参数为 None 表示立即关闭，也可以设置一个时间参数
        print("Server stopped.")
        # time.sleep(5)
        # self.running = False
        return ConnectManager_pb2.ShutDownResponse(response="shutdown")
        # sys.exit()

    def AddListenerOnRequestComponentStop(self, request, context):
        response = ConnectManager_pb2.AddListenerOnRequestComponentStopResponse(response="request component stop")
        yield response

    def ConfirmRequestComponentStop(self, request, context):
        print(request.request)
        return ConnectManager_pb2.ConfirmRequestComponentStopResponse(response="confirm request component stop")


class MessageManagerService(MessageManager_pb2_grpc.MessageManagerServiceServicer):

    def BindMessage(self, request, context):
        # 实现话题绑定逻辑
        return MessageManager_pb2.BindMessageResponse(serviceID='service_id', messageKey='service_id',
                                                      topic='service_id')

    def AddListenerOnBindMessage(self, request, context):
        for _ in range(3):
            print(request.request)
            response = MessageManager_pb2.AddListenerOnBindMessageResponse(serviceID='1', messageKey='2', topic='3')
            yield response
        # 实现话题绑定监听逻辑

    def ConfirmBindMessage(self, request, context):
        # 实现中控确认话题绑定逻辑
        return MessageManager_pb2.ConfirmBindMessageResponse(response="confirmed")

    def GetTopicByMessageKey(self, request, context):
        # 实现通过message_key获取topic逻辑
        topic = "your_topic"
        return MessageManager_pb2.GetTopicByMessageKeyResponse(topic='topic')

    def SubscribeTopic(self, request, context):
        for _ in range(3):
            # 实现话题订阅逻辑
            yield MessageManager_pb2.SubscribeTopicResponse(response=b'subscribed')

    def SendMessage(self, request_iterator, context):
        # 实现消息发送逻辑
        for req in request_iterator:
            # 处理每个streaming request
            print(req)
        return MessageManager_pb2.SendMessageResponse(response="sent")

    def SendResult(self, request, context):
        print(request)
        # 实现单次信息结果发送逻辑
        return MessageManager_pb2.SendResultResponse(response="result_sent")

    def UnsubscribeTopic(self, request, context):
        print(request)
        # 实现话题取消订阅逻辑
        return MessageManager_pb2.UnsubscribeTopicResponse(response="unsubscribed")


# 创建gRPC服务器
def serve_main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    ConfigManager_pb2_grpc.add_ConfigManagerServiceServicer_to_server(ConfigManagerService(), server)
    MessageManager_pb2_grpc.add_MessageManagerServiceServicer_to_server(MessageManagerService(), server)
    ComponmentManager_pb2_grpc.add_ComponentManagerServiceServicer_to_server(ComponentManagerService(), server)
    ConnectManager_pb2_grpc.add_ConnectManagerServiceServicer_to_server(ConnectManagerService(), server)
    server.add_insecure_port('localhost:9000')
    server.start()
    print("Server started. Listening on port 500577...")
    # while ConnectManagerService.running:
    server.wait_for_termination()


if __name__ == '__main__':
    serve_main()
