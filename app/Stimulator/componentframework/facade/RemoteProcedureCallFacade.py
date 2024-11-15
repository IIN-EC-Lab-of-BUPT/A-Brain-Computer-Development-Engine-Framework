from abc import ABC, abstractmethod
from injector import inject


class RemoteProcedureCallFacade(ABC):
    @inject
    def __init__(self):
        pass

    @abstractmethod
    async def startup(self, component_startup_configuration):
        pass
