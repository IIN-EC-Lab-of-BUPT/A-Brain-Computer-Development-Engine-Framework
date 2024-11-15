from dataclasses import dataclass
from typing import Union


@dataclass
class ApplicationExitControlModel:
    pass


@dataclass
class StartDataSendingControlModel:
    pass


@dataclass
class StopDataSendingControlModel:
    pass


@dataclass
class SendDeviceInfoControlModel:
    pass


@dataclass
class SendImpedanceControlModel:
    pass


@dataclass
class CollectorControlModel:
    package: Union[
        ApplicationExitControlModel,
        StartDataSendingControlModel,
        StopDataSendingControlModel,
        SendDeviceInfoControlModel,
        SendImpedanceControlModel,
    ] = None
