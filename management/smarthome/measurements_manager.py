from collections import namedtuple
from datetime import datetime, time, timedelta
from typing import List

from services.smart_home import SmartHomeBuilding

from .energy_calculators import sources_calculators
from .energy_manager import BuildingEnergyManager
from .models import (Device, EnergyDailyMeasurement, EnergyGenerator,
                     EnergyReceiver, EnergySourcesRaport)
from .serializers import BuildingSerializer


class EnergyMeasurementsManager:
    def __init__(self, building, energy_sources=sources_calculators):
        self._building = building
        self.measurements = None
        self._energy_manager = BuildingEnergyManager(self._building, energy_sources)

    def download_home_energy(self, start_date, end_date):
        time_diff = end_date - start_date
        diff_in_time_windows = time_diff.total_seconds() / 60 / 59
        current_start_date = start_date
        sources_raports = []
        measurements = []
        for hour in range(int(diff_in_time_windows)):
            current_start_date = start_date + timedelta(hours=hour)
            current_end_date = current_start_date + timedelta(minutes=59, seconds=59)
            measurements = self._get_energy_measurements(current_start_date, current_end_date)

            self._measurements = [data for data in measurements if data.datetime <= current_end_date and data.datetime >= current_start_date]

            measurements.append(self._measurements)
            energy_demand = self._get_energy_demand()
            energy_generated = self._get_energy_generated()
            sources = self._energy_manager.manage_energy_sources(
                current_end_date, energy_demand, energy_generated
            )
            sources_raports.append(
                EnergySourcesRaport(
                    building=self._building,
                    date_time_from=current_start_date,
                    date_time_to=current_end_date,
                    energy_sources=sources,
                )
            )
        return measurements, sources_raports

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

    def _get_energy_measurements(self, start_date: datetime, end_date: datetime):
        serialized_building = BuildingSerializer(self._building).data
        smart_building = SmartHomeBuilding(serialized_building)

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
