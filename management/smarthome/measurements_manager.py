from collections import namedtuple
from datetime import datetime, time, timedelta
from typing import List
from django.forms.models import model_to_dict

from services.smart_home import SmartHomeBuilding, SmartHomeEnergyStorage

from .energy_calculators import sources_calculators
from .constants import EnergySource as sources
from .energy_manager import BuildingEnergyManager
from .models import (Device, EnergyDailyMeasurement, EnergyGenerator,
                     EnergyReceiver, EnergySourcesRaport)


class EnergyMeasurementsManager:
    def __init__(self, building, energy_sources=sources_calculators):
        self._building = building
        self.measurements = None
        self._energy_manager = BuildingEnergyManager(self._building, energy_sources)

    def download_home_energy(self, start_date, end_date):
        time_diff = end_date - start_date
        diff_in_time_windows = time_diff.total_seconds() / 60 / 59
        current_start = start_date
        sources_raports = []
        surplus_raports = []
        measurements = []
        for hour in range(int(diff_in_time_windows)):
            current_start = start_date + timedelta(hours=hour)
            current_end = current_start + timedelta(minutes=59, seconds=59)

            measurements = self._get_energy_measurements(current_start, current_end)

            self._measurements = self._filter_correct_datetime_only(measurements, current_start, current_end)
            measurements.append(self._measurements)

            self._update_energy_manager_params(current_start, current_end)

            sources, surpluses = self._energy_manager.manage_energy_sources(self._get_energy_demand())

            surplus_raports.append(surpluses)
            sources_raports.append(
                EnergySourcesRaport(
                    building=self._building,
                    date_time_from=current_start,
                    date_time_to=current_end,
                    energy_sources=sources,
                )
            )
        return measurements, sources_raports, surplus_raports

    def _update_energy_manager_params(self, start_date, end_date):

        try:
            storage_measurements = self._get_storage_measurements(start_date, end_date)
            storage_measurements = self._filter_correct_datetime_only(storage_measurements, start_date, end_date)

            storage_usage_raports = self._get_storage_raports(start_date, end_date)
            storage_usage_raports = self._filter_correct_datetime_only(storage_usage_raports, start_date, end_date)
        except:
            storage_usage_raports = []
            storage_measurements = []

        home_energy_data = {
            "start_date": start_date, 
            "end_date": end_date,
            "energy_generated": self._get_energy_generated(),
            "storage_measurements": storage_measurements,
            "storage_usage_raports": storage_usage_raports,
        }
        self._energy_manager.update_home_energy_data(**home_energy_data)


    def _filter_correct_datetime_only(self, measurements, start_date, end_date):
        try:
            return [data for data in measurements if data.datetime <= end_date and data.datetime >= start_date]
        except AttributeError:
            try:
                return [data for data in measurements if data.date <= end_date and data.date >= start_date]
            except AttributeError:
                try:
                    return [data for data in measurements if data.date_time_from <= end_date and data.date_time_from >= start_date and data.date_time_to <= end_date and data.date_time_to >=start_date]
                except AttributeError:
                    return [data for data in measurements if data.date_time <= end_date and data.date_time >= start_date]


    def _bulk_create_daily_measurements(
        self, measurements: List[EnergyDailyMeasurement]
    ):
        return EnergyDailyMeasurement.objects.bulk_create(
            measurements, ignore_conflicts=True
        )

    def _get_energy_demand(self):
        return 0 - self._calculate_energy_sum(
            self._get_measurements_by_type(EnergyReceiver.__name__)
        )

    def _get_energy_generated(self):
        return self._calculate_energy_sum(
            self._get_measurements_by_type(EnergyGenerator.__name__)
        )

    def _calculate_energy_sum(self, measurements):
        return sum([data.energy_value for data in measurements])

    def _get_measurements_by_type(self, type_):
        return [data for data in self._measurements if data.device.type == type_]

    def _days_hours_minutes(self, td):
        time_diff = namedtuple("TimeDiff", "days hours minutes")
        return time_diff(td.days, td.seconds // 3600, (td.seconds // 60) % 60)

    def _get_storage_measurements(self, start_date: datetime, end_date: datetime):
        smart_building = SmartHomeBuilding(model_to_dict(self._building))
        storage_devices = smart_building.get_energy_storage(start_date, end_date)
        
        measurements=[]
        for device_data in storage_devices:
            device = Device.objects.get(id=device_data.get("device_id"))
            assert device.name == device_data.get("name")
            assert device.building.user.id == device_data.get("user")
            smart_device = SmartHomeEnergyStorage({**model_to_dict(device), "type": device.type})
            measurements+=smart_device.get_charge_state_raports(start_date, end_date)
        return measurements

    def _get_storage_raports(self, start_date: datetime, end_date: datetime):
        smart_building = SmartHomeBuilding(model_to_dict(self._building))
        storage_devices = smart_building.get_energy_storage(start_date, end_date)
        
        raports=[]
        for device_data in storage_devices:
            device = Device.objects.get(id=device_data.get("device_id"))
            assert device.name == device_data.get("name")
            assert device.building.user.id == device_data.get("user")
            smart_device = SmartHomeEnergyStorage({**model_to_dict(device), "type": device.type})
            raports+=smart_device.get_raports(start_date, end_date)
        return raports

    def _get_energy_measurements(self, start_date: datetime, end_date: datetime):
        smart_building = SmartHomeBuilding(model_to_dict(self._building))

        measurements = []

        day_energy_data = smart_building.get_energy_usage(start_date, end_date)

        for energy_data in day_energy_data:
            device_obj = Device.objects.get(id=energy_data["device_id"])
            measurements.append(
                EnergyDailyMeasurement(
                    device=device_obj,
                    datetime=end_date,
                    energy_value=energy_data.get("energy_value"),
                )
            )

        return measurements
