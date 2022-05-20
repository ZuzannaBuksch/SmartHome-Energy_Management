from enum import Enum
from typing import Any, Mapping

from .smart_object import SmartHomeObject


class SmartHomeDeviceRaport(SmartHomeObject):
    """Class that provides methods for requesting SmartHome device-raports selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.turned_on = data.get("turned_on")
        self.turned_off = data.get("turned_off")
        super().__init__(*args, **kwargs)

    @staticmethod
    def url(raport_url: int) -> str:
        return f"device-raports/{raport_url}/"

    def asdict(self):
        return {
            "id": self.id,
            "turned_on": self.turned_on,
            "turned_off": self.turned_off,
        }


class JobType(Enum):
    CHARGING = "CHARGING"
    USAGE = "USAGE"


class SmartHomeStorageChargingAndUsageRaport(SmartHomeObject):
    """Class that provides methods for requesting SmartHome storage-charging and usage raports selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.date_time_from = data.get("date_time_from")
        self.date_time_to = data.get("date_time_to")
        self.device = data.get("device")
        self.job_type = data.get("job_type")
        super().__init__(*args, **kwargs)

    @staticmethod
    def url(raport_url: int) -> str:
        return f"storage-raports/{raport_url}/"

    def asdict(self):
        return {
            "id": self.id,
            "date_time_from": self.date_time_from,
            "date_time_to": self.date_time_to,
            "job_type": self.job_type,
            "device": self.device,
        }
