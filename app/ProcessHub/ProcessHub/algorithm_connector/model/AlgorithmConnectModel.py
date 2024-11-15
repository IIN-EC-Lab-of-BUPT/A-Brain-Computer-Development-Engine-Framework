from dataclasses import dataclass


@dataclass
class AlgorithmConnectModel:
    address: str = None
    max_time_out: float = None
