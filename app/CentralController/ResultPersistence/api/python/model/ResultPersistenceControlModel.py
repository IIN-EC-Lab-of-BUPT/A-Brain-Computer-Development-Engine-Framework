from dataclasses import dataclass
from typing import Union


@dataclass
class ResultPersistenceExitControlModel:
    pass


@dataclass
class StartReceiveResultControlModel:
    pass


@dataclass
class StopReceiveResultControlModel:
    pass


@dataclass
class ResultPersistenceControlModel:
    package: Union[
        ResultPersistenceExitControlModel,
        StartReceiveResultControlModel,
        StopReceiveResultControlModel,
    ] = None
