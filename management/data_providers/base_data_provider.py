from abc import ABC
from datetime import datetime

class BaseDataProvider(ABC):
    _file_reader = None

    def get_data(self, date_time: datetime):
        raise NotImplementedError
