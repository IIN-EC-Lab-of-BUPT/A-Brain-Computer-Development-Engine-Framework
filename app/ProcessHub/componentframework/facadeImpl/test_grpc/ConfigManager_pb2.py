# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ConfigManager.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x43onfigManager.proto\x12/com.coreplantform.daemonproceed.controller.grpc\"*\n\x17ReadGlobalConfigRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\",\n\x18ReadGlobalConfigResponse\x12\x10\n\x08response\x18\x01 \x01(\t\"<\n)RegisterGlobalConfigUpdateCallbackRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\">\n*RegisterGlobalConfigUpdateCallbackResponse\x12\x10\n\x08\x63\x61llback\x18\x01 \x01(\t\",\n\x19UpdateGlobalConfigRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\".\n\x1aUpdateGlobalConfigResponse\x12\x10\n\x08response\x18\x01 \x01(\t\"9\n&CancelAddListenerOnGlobalConfigRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\";\n\'CancelAddListenerOnGlobalConfigResponse\x12\x10\n\x08response\x18\x01 \x01(\t2\xa9\x06\n\x14\x43onfigManagerService\x12\xa7\x01\n\x10ReadGlobalConfig\x12H.com.coreplantform.daemonproceed.controller.grpc.ReadGlobalConfigRequest\x1aI.com.coreplantform.daemonproceed.controller.grpc.ReadGlobalConfigResponse\x12\xdf\x01\n\"RegisterGlobalConfigUpdateCallback\x12Z.com.coreplantform.daemonproceed.controller.grpc.RegisterGlobalConfigUpdateCallbackRequest\x1a[.com.coreplantform.daemonproceed.controller.grpc.RegisterGlobalConfigUpdateCallbackResponse0\x01\x12\xad\x01\n\x12UpdateGlobalConfig\x12J.com.coreplantform.daemonproceed.controller.grpc.UpdateGlobalConfigRequest\x1aK.com.coreplantform.daemonproceed.controller.grpc.UpdateGlobalConfigResponse\x12\xd4\x01\n\x1f\x43\x61ncelAddListenerOnGlobalConfig\x12W.com.coreplantform.daemonproceed.controller.grpc.CancelAddListenerOnGlobalConfigRequest\x1aX.com.coreplantform.daemonproceed.controller.grpc.CancelAddListenerOnGlobalConfigResponseBG\n/com.coreplantform.daemonproceed.controller.grpcB\x12\x43onfigManagerProtoP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ConfigManager_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n/com.coreplantform.daemonproceed.controller.grpcB\022ConfigManagerProtoP\001'
  _globals['_READGLOBALCONFIGREQUEST']._serialized_start=72
  _globals['_READGLOBALCONFIGREQUEST']._serialized_end=114
  _globals['_READGLOBALCONFIGRESPONSE']._serialized_start=116
  _globals['_READGLOBALCONFIGRESPONSE']._serialized_end=160
  _globals['_REGISTERGLOBALCONFIGUPDATECALLBACKREQUEST']._serialized_start=162
  _globals['_REGISTERGLOBALCONFIGUPDATECALLBACKREQUEST']._serialized_end=222
  _globals['_REGISTERGLOBALCONFIGUPDATECALLBACKRESPONSE']._serialized_start=224
  _globals['_REGISTERGLOBALCONFIGUPDATECALLBACKRESPONSE']._serialized_end=286
  _globals['_UPDATEGLOBALCONFIGREQUEST']._serialized_start=288
  _globals['_UPDATEGLOBALCONFIGREQUEST']._serialized_end=332
  _globals['_UPDATEGLOBALCONFIGRESPONSE']._serialized_start=334
  _globals['_UPDATEGLOBALCONFIGRESPONSE']._serialized_end=380
  _globals['_CANCELADDLISTENERONGLOBALCONFIGREQUEST']._serialized_start=382
  _globals['_CANCELADDLISTENERONGLOBALCONFIGREQUEST']._serialized_end=439
  _globals['_CANCELADDLISTENERONGLOBALCONFIGRESPONSE']._serialized_start=441
  _globals['_CANCELADDLISTENERONGLOBALCONFIGRESPONSE']._serialized_end=500
  _globals['_CONFIGMANAGERSERVICE']._serialized_start=503
  _globals['_CONFIGMANAGERSERVICE']._serialized_end=1312
# @@protoc_insertion_point(module_scope)
