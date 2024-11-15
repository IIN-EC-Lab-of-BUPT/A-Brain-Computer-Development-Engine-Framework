from dataclasses import dataclass
from typing import Union


@dataclass
class ApplicationExitControlModel:
    pass


@dataclass
class ProcessHubControlModel:
    package: Union[
        ApplicationExitControlModel,
    ] = None
