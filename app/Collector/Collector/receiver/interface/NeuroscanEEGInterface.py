from abc import ABCMeta, abstractmethod


class NeuroScanEEGInterface(metaclass=ABCMeta):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_data(self):
        pass


    @abstractmethod
    def downSample(self, data):
        pass
