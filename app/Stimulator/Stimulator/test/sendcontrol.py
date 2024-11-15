# from Common.protobuf import CommonMessage_pb2, BaseDataClassMessage_pb2
# # from Common.protobuf.CommonMessage_pb2 import BaseDataMessageClass
# from Stimulator.api.protobuf.out import CommandControl_pb2
#
#
# class controller:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def start():
#         control = CommandControl_pb2
#         start = control.StartStimulationControlMessage()
#         serialized_start = start.SerializeToString()
#         return serialized_start
#
#     @staticmethod
#     def close():
#         control = CommandControl_pb2
#         close = control.StopStimulationControlMessage
#         serialized_close = close.SerializeToString()
#         return serialized_close
#
#     @staticmethod
#     def feedback():
#         data = CommonMessage_pb2.DataMessage
#         feedback = data.ResultPackage
#         a = BaseDataClassMessage_pb2.StringMessage
#         a.data = "hello world"
#         b = a.SerializeToString()
#         feedback.result = b
#         feedback.resultMessageClass = BaseDataMessageClass.STRING
#         c = CommonMessage_pb2.ReportSourceInformation
#         c.sourceLabel = "test"
#         c.position = 23.1
#         feedback.reportSourceInformation = c
#         return feedback.SerializeToString()
