from abc import ABC, abstractmethod


class ProxyInterface(ABC):

    @abstractmethod
    async def choice_start_block(self):
        """
        获取当前需要运行的block的id
        """
        pass

    @abstractmethod
    async def send_information(self):
        """
        获取当前需要运行的block的id
        """
        pass
