import numpy as np


class NeuroScanMessage():
    def __init__(self) -> None:
        # 初始化，定义各种请求类型
        self.initial()

    def initial(self):
        # infoType
        self.infoType = dict(
            InfoType_Version=1,
            InfoType_BasicInfo=2,
            InfoType_ChannelInfo=4
        )
        # dataType
        self.dataType = dict(
            Data_Info=1,
            Data_Eeg=2,
            Data_Event=3,
            Data_Impedance=4

        )
        # blockType
        self.blockType = dict(
            DataTypeFloat32bit=1,
            DataTypeEventList=3
        )
        # requestType
        self.requestType = dict(
            RequestVersion=1,
            RequestChannelInfo=3,
            RequestBasicInfoAcq=6,
            RequestStreamingStart=8,
            RequestStreamingStop=9
        )
        # controlCode
        self.controlType = dict(
            CTRL_FromServer=1,
            CTRL_FromClient=2,
        )

        return self

    def _convertMessage(self, chanID, code, request, samples, sizeBody, sizeUn):
        # 格式化
        self.chanID = np.fromstring(chanID, dtype='uint8')
        self.code = np.uint16([code])
        self.request = np.uint16([request])
        self.samples = np.uint32([samples])
        self.sizeBody = np.uint32([sizeBody])
        self.sizeUn = np.uint32([sizeUn])

        return self

    def initHeader(self, chanID, code, request, samples, sizeBody, sizeUn):
        self._convertMessage(chanID, code, request, samples, sizeBody, sizeUn)
        # chan
        chanFlow = self.chanID
        # code
        codeflow = self.code.byteswap().view(np.uint8)
        # request
        requestFlow = self.request.byteswap().view(np.uint8)
        # samples
        samples = self.samples.byteswap().view(np.uint8)
        # sizeBody
        sizeBody = self.sizeBody.byteswap().view(np.uint8)
        # sizeUn
        sizeUn = self.sizeUn.byteswap().view(np.uint8)

        # 拼接
        flow = np.concatenate((chanFlow, codeflow, requestFlow, samples, sizeBody, sizeUn))

        return flow

    # 构建header 用于传输请求类型
    def startStreaming(self):
        # start sending data
        # 28000
        header = self.initHeader(
            chanID='CTRL',
            code=self.controlType['CTRL_FromClient'],
            request=self.requestType['RequestStreamingStart'],
            samples=0, sizeBody=0, sizeUn=0
        )

        return header

    def getChannelInfo(self):
        # 23000
        header = self.initHeader(
            chanID='CTRL',
            code=self.controlType['CTRL_FromClient'],
            request=self.requestType['RequestChannelInfo'],
            samples=0, sizeBody=0, sizeUn=0
        )

        return header

    def getBasicInfo(self):
        # CTRL26000
        header = self.initHeader(
            chanID='CTRL',
            code=self.controlType['CTRL_FromClient'],
            request=self.requestType['RequestBasicInfoAcq'],
            samples=0, sizeBody=0, sizeUn=0
        )

        return header

class ChannelInfoOffsets():
    # 定义常量偏移量
    offset_channelId = 1
    offset_chanLabel = offset_channelId + 4
    offset_chanType = offset_chanLabel + 80
    offset_deviceType = offset_chanType + 4
    offset_eegGroup = offset_deviceType + 4
    offset_posX = offset_eegGroup + 4
    offset_posY = offset_posX + 8
    offset_posZ = offset_posY + 8
    offset_posStatus = offset_posZ + 8
    offset_bipolarRef = offset_posStatus + 4
    offset_addScale = offset_bipolarRef + 4
    offset_isDropDown = offset_addScale + 4
    offset_isNoFilter = offset_isDropDown + 4

    @staticmethod
    def get_chan_info_len():
        chanInfoLen = (ChannelInfoOffsets.offset_isNoFilter + 4) - 1
        chanInfoLen = round(chanInfoLen / 8) * 8
        return chanInfoLen

