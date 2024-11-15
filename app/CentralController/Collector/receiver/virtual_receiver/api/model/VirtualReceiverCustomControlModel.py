from dataclasses import dataclass
from typing import Union

from Common.model.CommonMessageModel import InformationPackageModel


@dataclass
class VirtualReceiverCustomControlModel:
    package: Union[
        InformationPackageModel
    ] = None
