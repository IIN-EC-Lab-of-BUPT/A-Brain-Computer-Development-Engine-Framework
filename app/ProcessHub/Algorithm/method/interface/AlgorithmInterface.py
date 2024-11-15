from abc import abstractmethod, ABC

from Algorithm.method.interface.ProxyInterface import ProxyInterface


class AlgorithmInterface(ABC):

    def __init__(self):
        self._proxy: ProxyInterface = None
        self._end_flag = False

    @abstractmethod
    async def run(self):
        pass

    def set_proxy(self, proxy: ProxyInterface):
        self._proxy = proxy

    def set_end_flag(self, end_flag: bool):
        self._end_flag = end_flag
