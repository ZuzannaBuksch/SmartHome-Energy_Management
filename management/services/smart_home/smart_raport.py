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
            "turned_off": self.turned_off
        }
    
