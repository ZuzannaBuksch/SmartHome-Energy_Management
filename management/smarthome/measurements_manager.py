from collections import namedtuple
from copy import deepcopy
from datetime import datetime, timedelta
from typing import List, OrderedDict

from django.forms.models import model_to_dict
from services.smart_home import SmartHomeBuilding, SmartHomeEnergyStorage

from .constants import EnergySource as sources
from .energy_calculators import (EnergyExchangeCalculator,
                                 EnergyStorageCalculator,
                                 GridSurplusEnergyCalculator,
                                 PhotovoltaicsEnergyCalculator,
                                 PublicGridEnergyCalculator)
from .energy_manager import BuildingEnergyManager
from .models import (Device, EnergyDailyMeasurement, EnergyGenerator,
                     EnergyReceiver, EnergySourcesRaport, EnergyStorage,
                     ExchangeEnergyStorageRaport,
                     PhotovoltaicsSufficiencyRaport)


class EnergyMeasurementsManager:
    def __init__(self, building, energy_sources=None):
        self._building = building
        self._measurements = None
        if not energy_sources:
            energy_sources = self._get_home_energy_sources()
        self._energy_manager = BuildingEnergyManager(self._building, energy_sources)

    def download_home_energy(self, start_date:datetime, end_date:datetime):
        time_diff = end_date - start_date
        diff_in_time_windows = time_diff.total_seconds() / 3600
        current_start = start_date
        sources_raports, surplus_raports, total_measurements, sufficiency_raports = [], [], [], []

        for hour in range(round(diff_in_time_windows)):
            current_start = start_date + timedelta(hours=hour)
            current_end = current_start + timedelta(minutes=59, seconds=59)

            measurements = self._get_energy_measurements(current_start, current_end)
            self._measurements = self._filter_correct_datetime_only(measurements, current_start, current_end)
            total_measurements+=self._measurements
            sufficiency_raport = self._get_photovoltaics_sufficiency_raport(current_end)
            sufficiency_raports.append(sufficiency_raport)

            self._update_energy_manager_params(current_start, current_end)
            sources, surpluses = self._energy_manager.manage_energy_sources(self._get_energy_demand())
            surplus_raports.append(surpluses)
            sources_raports.append(sources)
    
        self._bulk_create_daily_measurements(total_measurements)
        self._bulk_create_energy_sources_raports(sources_raports)
        self._bulk_create_photovoltaics_sufficiency_raports(sufficiency_raports)
        return total_measurements, sources_raports, surplus_raports


    def _update_energy_manager_params(self, start_date, end_date):
        try:
            storage_measurements = self._get_storage_measurements(start_date, end_date)
        except:
            storage_measurements = []

        home_energy_data = {
            "start_date": start_date, 
            "end_date": end_date,
            "energy_used": self._get_energy_demand(),
            "energy_generated": self._get_energy_generated(),
            "storage_measurements": storage_measurements,
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


    def _get_home_energy_sources(self):
        available_sources = []
        available_sources.append((sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator))          
        if self._building.use_exchange_energy:
            available_sources.append((sources.ENERGY_EXCHANGE, EnergyExchangeCalculator))
        available_sources.append((sources.GRID_SURPLUS, GridSurplusEnergyCalculator))
        if self._has_energy_storage():
            available_sources.append((sources.ENERGY_STORAGE, EnergyStorageCalculator))

        available_sources.append((sources.PUBLIC_GRID, PublicGridEnergyCalculator))
        end_sources = OrderedDict(available_sources)
        return end_sources

    def _has_energy_storage(self):
        return EnergyStorage.objects.filter(building=self._building).exists()

    def _has_photovoltaics(self):
        return EnergyGenerator.objects.filter(building=self._building).exists()


    def _bulk_create_energy_sources_raports(
        self, energy_sources_raports: List[EnergySourcesRaport]
    ):
        raports = deepcopy(energy_sources_raports)
        for raport in raports:
            raport.energy_sources = {k.value: v for k,v in raport.energy_sources.items()}
        
        return EnergySourcesRaport.objects.bulk_create(
            raports, ignore_conflicts=True
        )

    def _bulk_create_daily_measurements(
        self, measurements: List[EnergyDailyMeasurement]
    ):
        return EnergyDailyMeasurement.objects.bulk_create(
            measurements, ignore_conflicts=True
        )

    def _bulk_create_photovoltaics_sufficiency_raports(
        self, sufficiency_raports: List[PhotovoltaicsSufficiencyRaport]
        ):
        if self._has_photovoltaics():
            return PhotovoltaicsSufficiencyRaport.objects.bulk_create(
                sufficiency_raports, ignore_conflicts=True
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
        try:
            sum_ = sum([data.energy_value for data in measurements])
        except ValueError:
            sum_ = 0
        return sum_

    def _get_measurements_by_type(self, type_):
        return [data for data in self._measurements if data.device.type == type_]

    def _days_hours_minutes(self, td):
        time_diff = namedtuple("TimeDiff", "days hours minutes")
        return time_diff(td.days, td.seconds // 3600, (td.seconds // 60) % 60)

    def _get_photovoltaics_sufficiency_raport(self, date_time):
        energy_need = abs(self._get_energy_demand())
        energy_generated = self._get_energy_generated()
        try:
            percentage_sufficiency = 100*energy_generated/energy_need
        except ZeroDivisionError:
            percentage_sufficiency = None
        return PhotovoltaicsSufficiencyRaport(building=self._building, sufficiency_percentage=percentage_sufficiency, date_time=date_time)

    def _get_storage_measurements(self, start_date: datetime, end_date: datetime):
        if not self._has_energy_storage():
            return []
        smart_building = SmartHomeBuilding(model_to_dict(self._building))
        storage_devices = smart_building.get_energy_storage(start_date, end_date)
        measurements=[]
        for device_data in storage_devices:
            device = Device.objects.get(id=device_data.get("device_id"))
            smart_device = SmartHomeEnergyStorage({**model_to_dict(device), "type": device.type})
            raports = smart_device.get_charge_state_raports(start_date, end_date)
            for raport in raports:
                raport.device = device
            measurements+=raports
        return measurements

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
