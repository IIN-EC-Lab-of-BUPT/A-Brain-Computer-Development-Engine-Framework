from abc import ABC, abstractmethod
from typing import Union

from Algorithm.method.interface.SourceReceiverReaderInterface import SourceReceiverReaderInterface
from Algorithm.method.model.AlgorithmObject import AlgorithmResultObject


class ProxyInterface(ABC):

    @abstractmethod
    def get_source(self, source_label: str) -> SourceReceiverReaderInterface:
        pass

    @abstractmethod
    async def report(self, algorithm_result_object: AlgorithmResultObject):
        pass

    @abstractmethod
    def get_challenge_config(self) -> dict[str, Union[str, dict]]:
        pass
