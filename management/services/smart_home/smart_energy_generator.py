from typing import Any, Mapping

from .smart_device import SmartHomeDevice


class SmartHomeEnergyGenerator(SmartHomeDevice):
    """Class that provides methods for requesting SmartHome energy generating device selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.generation_power = data.get("generation_power")
        super().__init__(data, *args, **kwargs)

    def asdict(self):
        return {
            "generation_power": self.generation_power,
            **super().asdict()
        }
