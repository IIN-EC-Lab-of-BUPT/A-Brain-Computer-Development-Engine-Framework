from dataclasses import dataclass


@dataclass
class ExternalTriggerModel:
    """
    ExternalTriggerModel
    """
    timestamp: float = None
    trigger: str = None
