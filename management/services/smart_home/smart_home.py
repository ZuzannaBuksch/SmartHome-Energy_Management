from .smart_building import SmartHomeBuilding
from .smart_object import SmartHomeObject
from .smart_user import SmartHomeUser
from typing import List
from requests import Response
import json

class SmartHome(SmartHomeObject):
    """Class that provides method for requesting SmartHome users"""

    def get_user(self, user_id):
        data = self._get_data(SmartHomeUser.url(user_id))
        return SmartHomeUser(data, self._request)

    def push_users(self, users=List[SmartHomeUser]) -> Response:
        push_url = f"users/"
        users_data = [user.asdict() for user in users]
        for user in users_data:
            resp = self._push_data(push_url, data=json.dumps(user))
        return resp

    def get_building(self, building_id):
        data = self._get_data(SmartHomeBuilding.url(building_id))
        return SmartHomeBuilding(data, self._request)
