from .smart_building import SmartHomeBuilding
from .smart_object import SmartHomeObject
from .smart_user import SmartHomeUser


class SmartHome(SmartHomeObject):
    """Class that provides method for requesting SmartHome users"""

    def get_user(self, user_id):
        data = self._get_data(SmartHomeUser.url(user_id))
        return SmartHomeUser(data, self._request)

    def get_building(self, building_id):
        data = self._get_data(SmartHomeBuilding.url(building_id))
        return SmartHomeBuilding(data, self._request)
