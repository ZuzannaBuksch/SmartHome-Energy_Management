import json
from typing import Any, List, Mapping

from requests import Response

from .smart_building import SmartHomeBuilding
from .smart_object import SmartHomeObject


class SmartHomeUser(SmartHomeObject):
    """Class that provides methods for requesting SmartHome user selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.name = data.get("name")
        self.email = data.get("email")
        self.password = data.get("password")
        super().__init__(*args, **kwargs)

    @staticmethod
    def url(user_id: str) -> str:
        return f"users/{user_id}"

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
        }

    def get_buildings(self, building_id):
        data = self._get_data(SmartHomeBuilding.url(building_id))
        return [SmartHomeBuilding(building_data) for building_data in data]

    def push_buildings(self, buildings=List[SmartHomeBuilding]) -> Response:
        push_url = f"{SmartHomeUser.url(self.id)}/buildings/"
        buildings_data = [building.asdict() for building in buildings]
        return self._push_data(push_url, data=json.dumps(buildings_data))
