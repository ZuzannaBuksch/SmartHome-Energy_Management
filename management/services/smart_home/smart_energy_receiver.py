from typing import Any, Mapping

from .smart_device import SmartHomeDevice


class SmartHomeEnergyReceiver(SmartHomeDevice):
    """Class that provides methods for requesting SmartHome energy receiving device selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.device_power = data.get("device_power")
        self.supply_voltage = data.get("supply_voltage")
        super().__init__(data, *args, **kwargs)

    def asdict(self):
        return {
            "device_power": self.device_power,
            "supply_voltage": self.supply_voltage,
            **super().asdict(),
        }
