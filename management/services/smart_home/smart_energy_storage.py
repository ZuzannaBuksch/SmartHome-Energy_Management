import json
from datetime import datetime
from typing import Any, Mapping

from .smart_device import SmartHomeDevice
from .smart_raport import (SmartHomeChargeStateRaport,
                           SmartHomeStorageChargingAndUsageRaport)


class SmartHomeEnergyStorage(SmartHomeDevice):
    """Class that provides methods for requesting SmartHome energy storage device selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.capacity = data.get("capacity")
        self.battery_voltage = data.get("battery_voltage")
        super().__init__(data, *args, **kwargs)


    def asdict(self):
        return {
            "capacity": self.capacity,
            "battery_voltage": self.battery_voltage,
            **super().asdict(),
        }

    def get_raports(self, start_date: datetime, end_date: datetime):
        get_url = f"{SmartHomeEnergyStorage.url(self.id)}"
        self._request.start_date = start_date
        self._request.end_date = end_date
        device = self._get_data(get_url)
        raports = device.get("raports")
        return [
            SmartHomeStorageChargingAndUsageRaport(raport, self._request)
            for raport in raports
        ]

    def get_charge_state_raports(self, start_date: datetime, end_date: datetime):
        get_url = f"{SmartHomeEnergyStorage.url(self.id)}/charge-state-raports/"
        self._request.start_date = start_date
        self._request.end_date = end_date
        raports = self._get_data(get_url)
        return [
            SmartHomeChargeStateRaport(raport, self._request)
            for raport in raports
        ]
    
    def push_charge_state_raports(self, raports):
        push_url = f"{SmartHomeDevice.url(self.id)}/charge-state-raports/"
        raports_data = [raport.asdict() for raport in raports]
        return self._push_data(push_url, data=json.dumps(raports_data))

