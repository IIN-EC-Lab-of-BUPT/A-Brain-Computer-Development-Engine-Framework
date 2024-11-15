import grpc
from concurrent import futures
from Stimulator.facade.protobuf.out import ExternalTriggerService_pb2_grpc
import google.protobuf.empty_pb2 as empty_pb2


# 定义服务端类
class ExternalTriggerService(ExternalTriggerService_pb2_grpc.ExternalTriggerServiceServicer):

    def trigger(self, request, context):
        for req in request:
            # 处理每个streaming request
            print(req.trigger)
            print(req.timestamp)
            return empty_pb2.Empty()


# 创建gRPC服务器
def serve_main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    ExternalTriggerService_pb2_grpc.add_ExternalTriggerServiceServicer_to_server(ExternalTriggerService(), server)
    server.add_insecure_port('localhost:1017')
    server.start()
    print("Server started. Listening on port 1017...")
    # while ConnectManagerService.running:
    server.wait_for_termination()


if __name__ == '__main__':
    serve_main()
