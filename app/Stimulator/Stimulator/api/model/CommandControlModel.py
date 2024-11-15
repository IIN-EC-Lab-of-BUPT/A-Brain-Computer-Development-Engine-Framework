from dataclasses import dataclass
from typing import Union


@dataclass
class StartStimulationControlModel:
    pass


@dataclass
class StopStimulationControlModel:
    pass


@dataclass
class QuitStimulationControlModel:
    pass


@dataclass
class StimulationControlModel:
    package: Union[
        StartStimulationControlModel,
        StopStimulationControlModel,
        QuitStimulationControlModel
    ] = None
