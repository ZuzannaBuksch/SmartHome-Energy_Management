import json
from datetime import date, datetime, time, timedelta
from typing import Any, List, Mapping

from requests import Response
from smarthome.models import (Device, EnergyGenerator, EnergyReceiver,
                              EnergyStorage)

from .smart_device import SmartHomeDevice
from .smart_energy_generator import SmartHomeEnergyGenerator
from .smart_energy_receiver import SmartHomeEnergyReceiver
from .smart_energy_storage import SmartHomeEnergyStorage
from .smart_object import SmartHomeObject


class SmartHomeBuilding(SmartHomeObject):
    """Class that provides methods for requesting SmartHome building selected data"""

    def __init__(self, data: Mapping[str, Any], *args, **kwargs):
        self.id = data.get("id")
        self.name = data.get("name")
        self.icon = data.get("icon")
        super().__init__(*args, **kwargs)

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
        }

    @staticmethod
    def url(building_id: int = None) -> str:
        if not building_id:
            return "buildings/"
        return f"buildings/{building_id}"

    def _get_device_class(self, type):
        return {
            EnergyReceiver.__name__: SmartHomeEnergyReceiver,
            EnergyGenerator.__name__: SmartHomeEnergyGenerator,
            EnergyStorage.__name__: SmartHomeEnergyStorage,
        }.get(type)

    def get_devices(self):
        devices_url = f"{SmartHomeBuilding.url(self.id)}/devices/"
        data = self._get_data(devices_url)
        return [
            self._get_device_class(device.get("type"))(device, self._request)
            for device in data
        ]

    def push_devices(self, devices: List[SmartHomeDevice]) -> Response:
        push_url = f"{SmartHomeBuilding.url(self.id)}/devices/"
        devices_data = [device.asdict() for device in devices]
        return self._push_data(push_url, data=json.dumps(devices_data))


    def get_energy_usage(self, start_date: datetime, end_date: datetime):
        energy_url = f"{SmartHomeBuilding.url(self.id)}/energy"
        return self._get_energy(start_date, end_date, energy_url)
    
    def get_energy_storage(self, start_date: datetime, end_date: datetime):
        energy_url = f"{SmartHomeBuilding.url(self.id)}/energy-storage"
        return self._get_energy(start_date, end_date, energy_url)

    def get_energy_hour_by_hour(self, day=None):
        if day is None:
            day = date.today()
        dates = [datetime.combine(day, time(hour=x)) for x in range(24)]

        return {
            (dates[i] + timedelta(minutes=59, seconds=59)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ): self.get_energy_usage(dates[i], dates[i] + timedelta(minutes=59, seconds=59))
            for i in range(0, len(dates))
        }

    def _get_energy(self, start_date:datetime, end_date:datetime, energy_url:str):
        self._request.start_date = start_date
        self._request.end_date = end_date
        energy_data = self._get_data(energy_url)

        if not (self.name == energy_data.get("name")):
            error_data = {
                "Error": "Wrong building data is being downloaded from the simulation"
            }
            raise Exception(error_data)

        energy_measurements = []
        for device_data in energy_data.get("building_devices", []):
            try:
                device = Device.objects.get(id=device_data["id"])
                value = device_data.get("energy")
                energy_measurements.append(
                    {
                        "device_id": device.id,
                        "energy_value": value,
                        "date": end_date,
                    }
                )
            except Device.DoesNotExists:
                pass
        return energy_measurements
