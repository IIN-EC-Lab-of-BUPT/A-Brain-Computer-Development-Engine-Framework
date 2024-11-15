from dataclasses import dataclass
from typing import Union


@dataclass
class ApplicationExitControlModel:
    pass


@dataclass
class TaskControlModel:
    package: Union[
        ApplicationExitControlModel,
    ] = None
