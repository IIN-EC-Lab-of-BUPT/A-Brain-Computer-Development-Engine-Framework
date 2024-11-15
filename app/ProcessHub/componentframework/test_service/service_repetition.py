# """        2.1              """
# import grpc
# import test_pb2
# import test_pb2_grpc
# from concurrent import futures
#
#
# class ServiceConfigManagerService(test_pb2_grpc.ServiceConfigManagerServiceServicer):
#      def ReadGlobalConfig(self, request, context):
#         file_name = request.file_name
#         try:
#             with open(file_name, 'r') as file:
#                 xml_content = file.read()
#                 response = test_pb2.ConfigResponse1(xml_content=xml_content)
#                 return response
#         except FileNotFoundError:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details("File not found")
#
#
# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     test_pb2_grpc.add_ServiceConfigManagerServiceServicer_to_server(ServiceConfigManagerService(), server)
#     server.add_insecure_port('localhost:50051')
#     server.start()
#     print("Server started. Listening on port 50051...")
#     server.wait_for_termination()
#
#
# if __name__ == '__main__':
#     serve()


"""        2.2              """
import time

import grpc
import test_pb2
import test_pb2_grpc
from concurrent import futures


class ServiceConfigManagerService(test_pb2_grpc.ConfigManagerServiceServicer):
    def ReadGlobalConfig(self, request, context):
        print(request)
        dict_o = {"ReadGlobalConfig": "ReadGlobalConfigSuccessful", "ReadGlobalConfig1": "ReadGlobalConfigSuccessful1"}
        response = test_pb2.ReadUserConfigResponse(response=dict_o)
        return response
        # file_name = request.file_name
        # try:
        #     with open(file_name, 'r') as file:
        #         xml_content = file.read()
        #         response = test_pb2.ReadGlobalConfigResponse(xml_content=xml_content)
        #         return response
        # except FileNotFoundError:
        #     context.set_code(grpc.StatusCode.NOT_FOUND)
        #     context.set_details("File not found")

    def ReadUserConfig(self, request, context):
        print(request)
        rec_dict = {request.configKey: "1"}
        response = test_pb2.ReadUserConfigResponse(response=rec_dict)
        return response

    def RegisterGlobalConfigUpdateCallback(self, request, context):
        print(request)
        rec_dict={'request.config_key': '123'}
        for _ in range(2):
            response = test_pb2.RegisterGlobalConfigUpdateCallbackResponse(callback="rec_dict1")
            yield response
            time.sleep(2)
        # recieve_dict1 = dict(request.global_config_send)
        # print(recieve_dict1)
        # recieve_dict1['config_value'] = '123'
        # key = recieve_dict1['config_key'] + recieve_dict1['change_type']
        # recieve_dict1['key'] = key
        # print(recieve_dict1)
        # for _ in range(2):
        #     response = test_pb2.ConfigResponse3(global_config_rec=recieve_dict1)
        #     print(response)
        #     yield response
        #     print("fscg")
        #     time.sleep(2)

    def RegisterUserConfigUpdateCallback(self, request, context):
        recieve_dict1 = dict(request.user_config_send)
        recieve_dict1['config_value'] = '123'
        for _ in range(2):
            response = test_pb2.ConfigResponse4(user_config_rec=recieve_dict1)
            yield response
            print("fscg")
            time.sleep(2)

    def RegisterServiceEventCallback(self, request, context):
        recieve_dict1 = dict(request.service_event_send)
        recieve_dict1['event_value'] = '123'
        for _ in range(2):
            response = test_pb2.ConfigResponse5(service_event_rec=recieve_dict1)
            yield response
            print("fscg")
            time.sleep(2)

    def RegisterServiceTopicCallback(self, request, context):
        recieve_dict1 = dict(request.service_topic_send)
        recieve_dict1['message_value'] = '123'
        for _ in range(2):
            response = test_pb2.ConfigResponse6(service_topic_rec=recieve_dict1)
            yield response
            print("fscg")
            time.sleep(2)

    def RegisterSubscribeEventCallback(self, request, context):
        recieve_dict1 = dict(request.subscribe_event_send)
        recieve_dict1['event_value'] = '123'
        for _ in range(2):
            response = test_pb2.ConfigResponse7(subscribe_event_rec=recieve_dict1)
            yield response
            print("fscg")
            time.sleep(2)

    def RegisterSubscribeTopicCallback(self, request, context):
        recieve_dict1 = dict(request.subscribe_topic_send)
        recieve_dict1['message_value'] = '123'
        for _ in range(2):
            response = test_pb2.ConfigResponse8(subscribe_topic_rec=recieve_dict1)
            yield response
            print("fscg")
            time.sleep(2)

    def UpdateUserConfig(self, request, context):
        recieve_dict1 = dict(request.update_user_config_send)
        print(recieve_dict1)
        response = test_pb2.ConfigResponse9(update_user_config_rec='UpdateUserConfig  Successful')
        return response

    def UpdateGlobalConfig(self, request, context):
        recieve_dict1 = dict(request.update_global_config_send)
        print(recieve_dict1)
        response = test_pb2.ConfigResponse10(update_global_config_rec='UpdateGlobalConfig  Successful')
        return response


# class EventManagerService(test_pb2_grpc.EventManagerServiceServicer):
#     def CreateEvent(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict1['CreateEvent成功'] = 'fsck'
#         print(recieve_dict1)
#         response = test_pb2.ConfigResponse11(rec=recieve_dict1)
#         return response
#
#     def SubscribeEvent(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict1['成功'] = 'fsck'
#         print(recieve_dict1)
#         for _ in range(2):
#             response = test_pb2.ConfigResponse12(rec=recieve_dict1)
#             yield response
#             print("fscg")
#             time.sleep(2)
#
#     def TriggerEvent(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'TriggerEvent成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'event_key': recieve_dict1['event_key'], 'event_topic': '1525'}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse13(rec=recieve_dict)
#         return response
#
#     def GetEventStatus(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'GetEventStatus成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'event_key': recieve_dict1['event_key'], 'event_topic': '1525', 'state': '511556'}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse14(rec=recieve_dict)
#         return response
#
#     def SetEventStatus(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'SetEventStatus成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'event_key': recieve_dict1['event_key'], 'event_topic': '1525', 'state': recieve_dict1['state']}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse15(rec=recieve_dict)
#         return response
#
#     def SyncEvents(self, request, context):
#         recieve_string = request.service_id
#         recieve_dict = {'SyncEvents成功': 'fsck', 'service_id': recieve_string,
#                         'event_key': '1565', 'event_topic': '1525'}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse16(rec=recieve_dict)
#         return response
#
#     def EventSubscriptionSuccess(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'EventSubscriptionSuccess成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'event_key': recieve_dict1['event_key'], 'event_topic': '1525',
#                         'change_type': recieve_dict1['change_type']}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse17(rec='EventSubscriptionSuccess成功')
#         return response
#
#     def GetEventsByServiceId(self, request, context):
#         recieve_string = request.service_id
#         recieve_dict = {'GetEventsByServiceId成功': 'fsck', 'event_topic': '[1525,[56156,156],616]'}
#         print(recieve_string)
#         response = test_pb2.ConfigResponse18(rec=recieve_dict)
#         return response
#
#
# class MessageManagerService(test_pb2_grpc.MessageManagerServiceServicer):
#     def CreateTopic(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict1['CreateTopic成功'] = 'fsck'
#         print(recieve_dict1)
#         response = test_pb2.ConfigResponse19(rec=recieve_dict1)
#         return response
#
#     def SubscribeTopic(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict1['SubscribeTopic成功'] = 'fsck'
#         print(recieve_dict1)
#         for _ in range(2):
#             response = test_pb2.ConfigResponse20(rec=recieve_dict1)
#             yield response
#             print("fscg")
#             time.sleep(2)
#
#     async def SendMessage(self, request, context):
#         # recieve_dict1 = dict(request.send)
#         # print(recieve_dict1)
#         # response = test_pb2.ConfigResponse21(rec='SendMessage成功')
#         # return response
#         received_data = []
#         for request_data in await request.send:
#             print(request_data)
#         # response_message = "Received {} data points".format(len(received_data))
#         return test_pb2.ConfigResponse21(rec='SendMessage成功')
#
#     def GetTopicStatus(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'GetTopicStatus成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'message_key': recieve_dict1['message_key'], 'topic': '1525', 'state': '511556'}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse22(rec=recieve_dict)
#         return response
#
#     def SyncTopics(self, request, context):
#         recieve_string = request.send
#         recieve_dict = {'SyncTopics成功': 'fsck', 'service_id': recieve_string,
#                         'message_key': '545556', 'topic': '1525'}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse23(rec=recieve_dict)
#         return response
#
#     def TopicSubscriptionSuccess(self, request, context):
#         recieve_dict1 = dict(request.send)
#         recieve_dict = {'TopicSubscription成功': 'fsck', 'service_id': recieve_dict1['service_id'],
#                         'message_key': recieve_dict1['message_key'], 'topic': recieve_dict1['topic'],
#                         'change_type': recieve_dict1['change_type']}
#         print(recieve_dict)
#         response = test_pb2.ConfigResponse24(rec='TopicSubscription成功')
#         return response
#
#     def GetTopicsByServiceId(self, request, context):
#         recieve_string = request.send
#         recieve_dict = {'GetTopicsByServiceId成功': 'fsck', 'service_id': recieve_string,
#                         'topic': '[1525],[4525]',
#                         }
#         print(recieve_dict)
#         for _ in range(2):
#             response = test_pb2.ConfigResponse25(rec=recieve_dict)
#             yield response
#             time.sleep(2)
#         # for _ in range(2):
#         #     response = test_pb2.ConfigResponse20(rec=recieve_dict1)
#         #     yield response
#         #     print("fscg")
#         #     time.sleep(2)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    test_pb2_grpc.add_ConfigManagerServiceServicer_to_server(ServiceConfigManagerService(), server)
    # test_pb2_grpc.add_EventManagerServiceServicer_to_server(EventManagerService(), server)
    # test_pb2_grpc.add_MessageManagerServiceServicer_to_server(MessageManagerService(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    print("Server started. Listening on port 50051...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

"""        2.3              """
# import grpc
# import test_pb2
# import test_pb2_grpc
# from concurrent import futures
# import asyncio
# import time
# class ServiceConfigManagerService(test_pb2_grpc.ServiceConfigManagerServiceServicer):
#     def RegisterGlobalConfigUpdateCallback(self, request, context):
#         change_type = request.change_type
#         config_key = request.config_key
#         for _ in range(5):
#             response = test_pb2.ConfigResponse3(change_type=change_type, config_key=config_key, config_value="123")
#             yield response
#             print("fscg")
#             time.sleep(2)
#
#
# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     test_pb2_grpc.add_ServiceConfigManagerServiceServicer_to_server(ServiceConfigManagerService(), server)
#     server.add_insecure_port('localhost:50051')
#     server.start()
#     print("Server started. Listening on port 50051...")
#     server.wait_for_termination()
#
#
# if __name__ == '__main__':
#     serve()
"""        2.4              """
# import grpc
# import test_pb2
# import test_pb2_grpc
# from concurrent import futures
# import asyncio
# import time
#
#
# class ServiceConfigManagerService(test_pb2_grpc.ServiceConfigManagerServiceServicer):
#     def __init__(self):
#         self.config_key = None
#         self.change_type = None
#         self.service_id = None
#
#     def RegisterUserConfigUpdateCallback(self, request, context):
#         self.service_id = request.service_id
#         self.change_type = request.change_type
#         self.config_key = request.config_key
#         for _ in range(5):
#             response = test_pb2.ConfigResponse4(service_id=self.service_id, config_key=self.config_key,change_type=self.change_type,
#                                                 config_value="12")
#             yield response
#             print("fscg")
#             time.sleep(2)
#
#
# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     test_pb2_grpc.add_ServiceConfigManagerServiceServicer_to_server(ServiceConfigManagerService(), server)
#     server.add_insecure_port('localhost:50051')
#     server.start()
#     print("Server started. Listening on port 50051...")
#     server.wait_for_termination()
#
#
# if __name__ == '__main__':
#     serve()
"""         2.5             """

# import grpc
# import test_pb2
# import test_pb2_grpc
# from concurrent import futures
# import asyncio
# import time
#
#
# class ServiceConfigManagerService(test_pb2_grpc.ServiceConfigManagerServiceServicer):
#     def __init__(self):
#         self.config_key = None
#         self.change_type = None
#         self.service_id = None
#
#     def RegisterServiceEventCallback(self, request, context):
#         self.service_id = request.service_id
#         self.change_type = request.change_type
#         self.event_key = request.event_key
#         for _ in range(5):
#             response = test_pb2.ConfigResponse5(service_id=self.service_id, event_key=self.event_key,change_type=self.change_type,
#                                                 event_value="12")
#             yield response
#             print("fscg")
#             time.sleep(2)
#
#
# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     test_pb2_grpc.add_ServiceConfigManagerServiceServicer_to_server(ServiceConfigManagerService(), server)
#     server.add_insecure_port('localhost:50051')
#     server.start()
#     print("Server started. Listening on port 50051...")
#     server.wait_for_termination()
#
#
# if __name__ == '__main__':
#     serve()
"""        2.9              """
# import grpc
# from concurrent import futures
# from test_pb2 import Request9, ConfigResponse9
# from test_pb2_grpc import ServiceConfigManagerServiceServicer, add_ServiceConfigManagerServiceServicer_to_server
#
# class ConfigManagerServicer(ServiceConfigManagerServiceServicer):
#     def UpdateUserConfig(self, Request9, context):
#         # 在这里处理接收到的 ConfigMessage 对象
#         xml_content = Request9.service_id
#         print("Received xml_content:", xml_content)
#
#         # 创建并返回 ConfigResponse 对象
#         response = ConfigResponse9()
#         response.status = "Success"
#         return response
#
# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     add_ServiceConfigManagerServiceServicer_to_server(ConfigManagerServicer(), server)
#     server.add_insecure_port('localhost:50051')
#     server.start()
#     server.wait_for_termination()
#
# if __name__ == '__main__':
#     serve()
