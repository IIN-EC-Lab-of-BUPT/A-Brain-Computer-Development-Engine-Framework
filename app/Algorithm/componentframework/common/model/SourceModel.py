from dataclasses import dataclass


@dataclass
class SourceModel(object):
    source_label: str = None
    source_topic: str = None
