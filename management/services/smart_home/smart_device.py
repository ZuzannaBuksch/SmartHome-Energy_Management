from datetime import datetime
import json
from typing import Any, Mapping
from .smart_raport import SmartHomeStorageChargingAndUsageRaport, SmartHomeDeviceRaport


from .smart_object import SmartHomeObject


class SmartHomeDevice(SmartHomeObject):
    """Class that provides methods for requesting SmartHome device selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.name = data.get("name")
        self.state = data.get("state")
        self.type = data.get("type")
        self.building = data.get("building")
        super().__init__(*args, **kwargs)

    @staticmethod
    def url(device_id: int) -> str:
        return f"devices/{device_id}/"

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "building": self.building,
            "resourcetype": self.type,
        }

    def update_state(self):
        return self._patch_data(
            SmartHomeDevice.url(self.id), data=json.dumps(self.asdict())
        )

    def get_raports(self, start_date: datetime, end_date: datetime):
        get_url = f"{SmartHomeDevice.url(self.id)}"
        self._request.start_date = start_date
        self._request.end_date = end_date
        device = self._get_data(get_url)
        raports = device.get("raports", [])
        raport_class = {
            "EnergyStorage": SmartHomeStorageChargingAndUsageRaport,
            "EnergyReceiver": SmartHomeDeviceRaport,
        }.get(self.type)
        return [raport_class(raport, self._request) for raport in raports]

    def push_raports(self, raports):
        push_url = f"{SmartHomeDevice.url(self.id)}/device-raports/"
        raports_data = [raport.asdict() for raport in raports]
        return self._push_data(push_url, data=json.dumps(raports_data))
