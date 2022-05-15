from typing import Any, Mapping

from .smart_device import SmartHomeDevice


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
            **super().asdict()
        }
