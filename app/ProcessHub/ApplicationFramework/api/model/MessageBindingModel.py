from dataclasses import dataclass


@dataclass
class MessageBindingModel:
    component_id: str = None
    message_key: str = None
    topic: str = None
