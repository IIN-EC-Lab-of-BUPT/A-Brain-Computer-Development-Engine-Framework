# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import componentframework.facadeImpl.test_grpc.ComponmentManager_pb2 as ComponmentManager__pb2

GRPC_GENERATED_VERSION = '1.64.1'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in ComponmentManager_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class ComponentManagerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/RegisterComponent',
                request_serializer=ComponmentManager__pb2.RegisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.RegisterComponentResponse.FromString,
                _registered_method=True)
        self.GetComponentInfo = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetComponentInfo',
                request_serializer=ComponmentManager__pb2.GetComponentInfoRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.GetComponentInfoResponse.FromString,
                _registered_method=True)
        self.AddListenerOnRegisterComponent = channel.unary_stream(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnRegisterComponent',
                request_serializer=ComponmentManager__pb2.AddListenerOnRegisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.AddListenerOnRegisterComponentResponse.FromString,
                _registered_method=True)
        self.UpdateComponentInfo = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UpdateComponentInfo',
                request_serializer=ComponmentManager__pb2.UpdateComponentInfoRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.UpdateComponentInfoResponse.FromString,
                _registered_method=True)
        self.AddListenerOnUpdateComponentInfo = channel.unary_stream(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUpdateComponentInfo',
                request_serializer=ComponmentManager__pb2.AddListenerOnUpdateComponentInfoRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.AddListenerOnUpdateComponentInfoResponse.FromString,
                _registered_method=True)
        self.UnregisterComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UnregisterComponent',
                request_serializer=ComponmentManager__pb2.UnregisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.UnregisterComponentResponse.FromString,
                _registered_method=True)
        self.AddListenerOnUnregisterComponent = channel.unary_stream(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUnregisterComponent',
                request_serializer=ComponmentManager__pb2.ComponentUnregisteredListenerRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.ComponentUnregisteredListenerResponse.FromString,
                _registered_method=True)
        self.GetAllComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetAllComponent',
                request_serializer=ComponmentManager__pb2.GetAllComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.GetAllComponentResponse.FromString,
                _registered_method=True)
        self.ConfirmComponentUnregister = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/ConfirmComponentUnregister',
                request_serializer=ComponmentManager__pb2.ConfirmComponentUnregisterRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.ConfirmComponentUnregisterResponse.FromString,
                _registered_method=True)
        self.GetComponentState = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetComponentState',
                request_serializer=ComponmentManager__pb2.GetComponentStateRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.GetComponentStateResponse.FromString,
                _registered_method=True)
        self.AddListenerOnUpdateComponentState = channel.unary_stream(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUpdateComponentState',
                request_serializer=ComponmentManager__pb2.AddListenerOnUpdateComponentStateRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.AddListenerOnUpdateComponentStateResponse.FromString,
                _registered_method=True)
        self.UpdateComponentState = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UpdateComponentState',
                request_serializer=ComponmentManager__pb2.UpdateComponentStateRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.UpdateComponentStateResponse.FromString,
                _registered_method=True)
        self.CancelAddListenerOnUnregisterComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUnregisterComponent',
                request_serializer=ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentResponse.FromString,
                _registered_method=True)
        self.CancelAddListenerOnUpdateComponentInfo = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUpdateComponentInfo',
                request_serializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoResponse.FromString,
                _registered_method=True)
        self.CancelAddListenerOnRegisterComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnRegisterComponent',
                request_serializer=ComponmentManager__pb2.CancelAddListenerOnRegisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.CancelAddListenerOnRegisterComponentResponse.FromString,
                _registered_method=True)
        self.CancelAddListenerOnUpdateComponentState = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUpdateComponentState',
                request_serializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateResponse.FromString,
                _registered_method=True)
        self.ConfirmRegisterComponent = channel.unary_unary(
                '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/ConfirmRegisterComponent',
                request_serializer=ComponmentManager__pb2.ConfirmRegisterComponentRequest.SerializeToString,
                response_deserializer=ComponmentManager__pb2.ConfirmRegisterComponentResponse.FromString,
                _registered_method=True)


class ComponentManagerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterComponent(self, request, context):
        """2.6.1.	组件注册
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetComponentInfo(self, request, context):
        """2.6.2.	获取指定组件信息：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddListenerOnRegisterComponent(self, request, context):
        """2.6.3.	组件注册监听回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateComponentInfo(self, request, context):
        """2.6.4.	修改组件配置信息：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddListenerOnUpdateComponentInfo(self, request, context):
        """2.6.5.	监听组件组件配置信息更新回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UnregisterComponent(self, request, context):
        """2.6.6.	组件注销
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddListenerOnUnregisterComponent(self, request, context):
        """2.6.7.	组件注销监听
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllComponent(self, request, context):
        """2.6.8.	获取所有组件信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ConfirmComponentUnregister(self, request, context):
        """2.6.9.	组件注销确认
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetComponentState(self, request, context):
        """2.6.10.	获取组件状态
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddListenerOnUpdateComponentState(self, request, context):
        """2.6.11.	组件状态更新监听
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateComponentState(self, request, context):
        """2.6.12.	更新组件状态
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelAddListenerOnUnregisterComponent(self, request, context):
        """2.6.13.	取消监听组件注销更新回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelAddListenerOnUpdateComponentInfo(self, request, context):
        """2.6.14.	取消监听组件配置信息更新回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelAddListenerOnRegisterComponent(self, request, context):
        """2.6.15.	取消监听组件注册更新回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelAddListenerOnUpdateComponentState(self, request, context):
        """2.6.16.	取消监听组件状态更新回调：
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ConfirmRegisterComponent(self, request, context):
        """2.6.17.	确认组件注册
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ComponentManagerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterComponent,
                    request_deserializer=ComponmentManager__pb2.RegisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.RegisterComponentResponse.SerializeToString,
            ),
            'GetComponentInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetComponentInfo,
                    request_deserializer=ComponmentManager__pb2.GetComponentInfoRequest.FromString,
                    response_serializer=ComponmentManager__pb2.GetComponentInfoResponse.SerializeToString,
            ),
            'AddListenerOnRegisterComponent': grpc.unary_stream_rpc_method_handler(
                    servicer.AddListenerOnRegisterComponent,
                    request_deserializer=ComponmentManager__pb2.AddListenerOnRegisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.AddListenerOnRegisterComponentResponse.SerializeToString,
            ),
            'UpdateComponentInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateComponentInfo,
                    request_deserializer=ComponmentManager__pb2.UpdateComponentInfoRequest.FromString,
                    response_serializer=ComponmentManager__pb2.UpdateComponentInfoResponse.SerializeToString,
            ),
            'AddListenerOnUpdateComponentInfo': grpc.unary_stream_rpc_method_handler(
                    servicer.AddListenerOnUpdateComponentInfo,
                    request_deserializer=ComponmentManager__pb2.AddListenerOnUpdateComponentInfoRequest.FromString,
                    response_serializer=ComponmentManager__pb2.AddListenerOnUpdateComponentInfoResponse.SerializeToString,
            ),
            'UnregisterComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.UnregisterComponent,
                    request_deserializer=ComponmentManager__pb2.UnregisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.UnregisterComponentResponse.SerializeToString,
            ),
            'AddListenerOnUnregisterComponent': grpc.unary_stream_rpc_method_handler(
                    servicer.AddListenerOnUnregisterComponent,
                    request_deserializer=ComponmentManager__pb2.ComponentUnregisteredListenerRequest.FromString,
                    response_serializer=ComponmentManager__pb2.ComponentUnregisteredListenerResponse.SerializeToString,
            ),
            'GetAllComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllComponent,
                    request_deserializer=ComponmentManager__pb2.GetAllComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.GetAllComponentResponse.SerializeToString,
            ),
            'ConfirmComponentUnregister': grpc.unary_unary_rpc_method_handler(
                    servicer.ConfirmComponentUnregister,
                    request_deserializer=ComponmentManager__pb2.ConfirmComponentUnregisterRequest.FromString,
                    response_serializer=ComponmentManager__pb2.ConfirmComponentUnregisterResponse.SerializeToString,
            ),
            'GetComponentState': grpc.unary_unary_rpc_method_handler(
                    servicer.GetComponentState,
                    request_deserializer=ComponmentManager__pb2.GetComponentStateRequest.FromString,
                    response_serializer=ComponmentManager__pb2.GetComponentStateResponse.SerializeToString,
            ),
            'AddListenerOnUpdateComponentState': grpc.unary_stream_rpc_method_handler(
                    servicer.AddListenerOnUpdateComponentState,
                    request_deserializer=ComponmentManager__pb2.AddListenerOnUpdateComponentStateRequest.FromString,
                    response_serializer=ComponmentManager__pb2.AddListenerOnUpdateComponentStateResponse.SerializeToString,
            ),
            'UpdateComponentState': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateComponentState,
                    request_deserializer=ComponmentManager__pb2.UpdateComponentStateRequest.FromString,
                    response_serializer=ComponmentManager__pb2.UpdateComponentStateResponse.SerializeToString,
            ),
            'CancelAddListenerOnUnregisterComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelAddListenerOnUnregisterComponent,
                    request_deserializer=ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentResponse.SerializeToString,
            ),
            'CancelAddListenerOnUpdateComponentInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelAddListenerOnUpdateComponentInfo,
                    request_deserializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoRequest.FromString,
                    response_serializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoResponse.SerializeToString,
            ),
            'CancelAddListenerOnRegisterComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelAddListenerOnRegisterComponent,
                    request_deserializer=ComponmentManager__pb2.CancelAddListenerOnRegisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.CancelAddListenerOnRegisterComponentResponse.SerializeToString,
            ),
            'CancelAddListenerOnUpdateComponentState': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelAddListenerOnUpdateComponentState,
                    request_deserializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateRequest.FromString,
                    response_serializer=ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateResponse.SerializeToString,
            ),
            'ConfirmRegisterComponent': grpc.unary_unary_rpc_method_handler(
                    servicer.ConfirmRegisterComponent,
                    request_deserializer=ComponmentManager__pb2.ConfirmRegisterComponentRequest.FromString,
                    response_serializer=ComponmentManager__pb2.ConfirmRegisterComponentResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ComponentManagerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/RegisterComponent',
            ComponmentManager__pb2.RegisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.RegisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetComponentInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetComponentInfo',
            ComponmentManager__pb2.GetComponentInfoRequest.SerializeToString,
            ComponmentManager__pb2.GetComponentInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddListenerOnRegisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnRegisterComponent',
            ComponmentManager__pb2.AddListenerOnRegisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.AddListenerOnRegisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateComponentInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UpdateComponentInfo',
            ComponmentManager__pb2.UpdateComponentInfoRequest.SerializeToString,
            ComponmentManager__pb2.UpdateComponentInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddListenerOnUpdateComponentInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUpdateComponentInfo',
            ComponmentManager__pb2.AddListenerOnUpdateComponentInfoRequest.SerializeToString,
            ComponmentManager__pb2.AddListenerOnUpdateComponentInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UnregisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UnregisterComponent',
            ComponmentManager__pb2.UnregisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.UnregisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddListenerOnUnregisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUnregisterComponent',
            ComponmentManager__pb2.ComponentUnregisteredListenerRequest.SerializeToString,
            ComponmentManager__pb2.ComponentUnregisteredListenerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetAllComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetAllComponent',
            ComponmentManager__pb2.GetAllComponentRequest.SerializeToString,
            ComponmentManager__pb2.GetAllComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ConfirmComponentUnregister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/ConfirmComponentUnregister',
            ComponmentManager__pb2.ConfirmComponentUnregisterRequest.SerializeToString,
            ComponmentManager__pb2.ConfirmComponentUnregisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetComponentState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/GetComponentState',
            ComponmentManager__pb2.GetComponentStateRequest.SerializeToString,
            ComponmentManager__pb2.GetComponentStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddListenerOnUpdateComponentState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/AddListenerOnUpdateComponentState',
            ComponmentManager__pb2.AddListenerOnUpdateComponentStateRequest.SerializeToString,
            ComponmentManager__pb2.AddListenerOnUpdateComponentStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateComponentState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/UpdateComponentState',
            ComponmentManager__pb2.UpdateComponentStateRequest.SerializeToString,
            ComponmentManager__pb2.UpdateComponentStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CancelAddListenerOnUnregisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUnregisterComponent',
            ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.CancelAddListenerOnUnregisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CancelAddListenerOnUpdateComponentInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUpdateComponentInfo',
            ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoRequest.SerializeToString,
            ComponmentManager__pb2.CancelAddListenerOnUpdateComponentInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CancelAddListenerOnRegisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnRegisterComponent',
            ComponmentManager__pb2.CancelAddListenerOnRegisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.CancelAddListenerOnRegisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CancelAddListenerOnUpdateComponentState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/CancelAddListenerOnUpdateComponentState',
            ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateRequest.SerializeToString,
            ComponmentManager__pb2.CancelAddListenerOnUpdateComponentStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ConfirmRegisterComponent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.coreplantform.daemonproceed.controller.grpc.ComponentManagerService/ConfirmRegisterComponent',
            ComponmentManager__pb2.ConfirmRegisterComponentRequest.SerializeToString,
            ComponmentManager__pb2.ConfirmRegisterComponentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
