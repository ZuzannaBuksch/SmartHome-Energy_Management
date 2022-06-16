from enum import Enum
from typing import Any, Mapping
from datetime import datetime
from .smart_object import SmartHomeObject


class SmartHomeDeviceRaport(SmartHomeObject):
    """Class that provides methods for requesting SmartHome device-raports selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        try:
            self.turned_on = datetime.strptime(data.get("turned_on"),"%Y-%m-%dT%H:%M:%S")
            self.turned_off = datetime.strptime(data.get("turned_off"),"%Y-%m-%dT%H:%M:%S")
        except TypeError:
            self.turned_on = data.get("turned_on")
            self.turned_off = data.get("turned_off")
        self.device = data.get("device")
        super().__init__(*args, **kwargs)

    def asdict(self):
        return {
            "id": self.id,
            "turned_on": self.turned_on.strftime("%Y-%m-%d %H:%M:%S"),
            "turned_off": self.turned_off.strftime("%Y-%m-%d %H:%M:%S")
        }


class JobType(Enum):
    CHARGING = "CHARGING"
    USAGE = "USAGE"


class SmartHomeStorageChargingAndUsageRaport(SmartHomeObject):
    """Class that provides methods for requesting SmartHome storage-charging and usage raports selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        try:
            self.date_time_from = datetime.strptime(data.get("date_time_from"),"%Y-%m-%dT%H:%M:%S")
            self.date_time_to = datetime.strptime(data.get("date_time_to"),"%Y-%m-%dT%H:%M:%S")
        except TypeError:
            self.date_time_from = data.get("date_time_from")
            self.date_time_to = data.get("date_time_to")
        self.job_type = data.get("job_type")
        self.energy_use = data.get("energy_use")
        super().__init__(*args, **kwargs)

    def asdict(self):
        return {
            "id": self.id,
            "date_time_from": self.date_time_from.strftime("%Y-%m-%d %H:%M:%S"),
            "date_time_to": self.date_time_to.strftime("%Y-%m-%d %H:%M:%S"),
            "job_type": self.job_type,
            "energy_use": self.energy_use,
        }


class SmartHomeChargeStateRaport(SmartHomeObject):
    """Class that provides methods for requesting SmartHome storage charge state raports selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.device = data.get("device")
        try:
            self.date = datetime.strptime(data.get("date"),"%Y-%m-%dT%H:%M:%S")
        except TypeError:
            self.date = data.get("date")
        self.charge_value = data.get("charge_value")
        super().__init__(*args, **kwargs)


    def asdict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "charge_value": self.charge_value
        }
