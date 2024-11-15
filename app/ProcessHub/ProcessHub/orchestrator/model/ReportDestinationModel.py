from dataclasses import dataclass


@dataclass
class ReportDestinationModel:
    report_key: str = None
    report_topic: str = None
