from Common.protobuf.CommonMessage_pb2 import InformationPackage as InformationPackage_pb2


class sendinformation:
    def __init__(self):
        pass

    @staticmethod
    def recieve(data):
        a = InformationPackage_pb2()
        c = a.ParseFromString(data)
        print(a)