from dataclasses import dataclass


@dataclass
class DataFileModel:
    subject_id: str = None
    file_path: str = None
