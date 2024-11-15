from dataclasses import dataclass
from typing import Union


@dataclass
class EEGPersistenceExitControlModel:
    pass


@dataclass
class StartReceiveEEGControlModel:
    pass


@dataclass
class StopReceiveEEGControlModel:
    pass


@dataclass
class EEGPersistenceControlModel:
    package: Union[
        EEGPersistenceExitControlModel,
        StartReceiveEEGControlModel,
        StopReceiveEEGControlModel,
    ] = None
