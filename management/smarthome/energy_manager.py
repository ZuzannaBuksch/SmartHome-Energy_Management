from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from services.smart_home import SmartHomeBuilding

from .models import Device, EnergyDailyMeasurement, EnergyGenerator, EnergyReceiver, EnergySourcesRaport, EnergySurplusRaport
from .price_classifier import PriceClassifier
from .grid_surplus_calc import GridSurplusEnergyCalculator
from .photovoltaics_calc import PhotovoltaicsEnergyCalculator
from .serializers import BuildingSerializer
from .constants import EnergySource as sources


class BuildingEnergyManager:
    _PUBLIC_GRID_PRICE = 0.68 #PLN
    _PHOTOVOLTAICS_PRICE = 0.0
    _GRID_SURPLUS_PRICE = 0.0
    _photovoltaics_calc = None
    _grid_surplus_calc = None

    def __init__(self, building):
        self._building = building
        self._grid_surplus_calc = GridSurplusEnergyCalculator(self._building)
        self._photovoltaics_calc = PhotovoltaicsEnergyCalculator()

    def manage_building_energy(self, start_date: datetime, end_date: datetime):
        measurements = self._download_energy_data_task_tmp(start_date, end_date)
        self._energy_sources = {}
        self._grid_surplus_calc.update_datetime(end_date)

        energy_missing = self._use_energy_from_source(sources.PHOTOVOLTAICS, measurements)
        energy_missing = self._use_energy_from_source(sources.GRID_SURPLUS, energy_missing)
        energy_missing = self._use_energy_from_source(sources.PUBLIC_GRID, energy_missing)

        sources_raport = EnergySourcesRaport(building=self._building, date_time_from = start_date, date_time_to=end_date, energy_sources=self._energy_sources)
        return measurements, sources_raport

    def _use_energy_from_source(self, source_type, *args, **kwargs):
        return {
            sources.PHOTOVOLTAICS: self._use_photovoltaics_energy,
            sources.GRID_SURPLUS: self._use_grid_surplus_energy,
            sources.PUBLIC_GRID: self._use_public_grid_energy,
        }.get(source_type)(*args, **kwargs)

    def _use_public_grid_energy(self, energy_demand):
        self._update_energy_sources(sources.PUBLIC_GRID, abs(energy_demand), self._PUBLIC_GRID_PRICE)

    def _use_grid_surplus_energy(self, energy_demand):
        energy_used, energy_missing =  self._grid_surplus_calc.calculate_grid_surplus_cover(energy_demand)
        self._update_energy_sources(sources.GRID_SURPLUS, energy_used, self._GRID_SURPLUS_PRICE) 
        return energy_missing 

    def _use_photovoltaics_energy(self, measurements):
        energy_generated = self._calculate_energy_sum(self._get_measurements_by_type(measurements, EnergyGenerator.__name__))
        energy_demand = self._calculate_energy_sum(self._get_measurements_by_type(measurements, EnergyReceiver.__name__))
        energy_used, energy_missing = self._photovoltaics_calc.calculate_photovoltaics_cover(energy_generated, energy_demand)
        self._update_energy_sources(sources.PHOTOVOLTAICS, energy_used, self._PHOTOVOLTAICS_PRICE)
        return energy_missing

    def _update_energy_sources(self, source, value, price, sources={}):
        grosze = Decimal('0.01')
        full_price = price*float(value)
        self._energy_sources[source] = {
            "value": value,
            "price": Decimal(full_price).quantize(grosze, ROUND_HALF_UP)
        }

    def _get_measurements_by_type(self, measurements, type_):
        return [data for data in measurements if data.device.type==type_]

    def _calculate_energy_sum(self, measurements):
        return sum([data.energy_value for data in measurements])

    def _bulk_create_daily_measurements(
        self, measurements: List[EnergyDailyMeasurement]
    ):
        return EnergyDailyMeasurement.objects.bulk_create(
            measurements, ignore_conflicts=True
        )

    def _download_energy_data_task(self, start_date: datetime, end_date: datetime):
        serialized_building = BuildingSerializer(self._building).data
        smart_building = SmartHomeBuilding(serialized_building)

        measurements = []
        days = [
            start_date + timedelta(days=x)
            for x in range((end_date - start_date).days + 1)
        ]
        hours = [hour for hour in range(0, 24)]
        for day in days:
            for hour in hours:
                start_datetime = datetime.combine(day, time(hour, 0, 0))
                end_datetime = datetime.combine(day, time(hour, 59, 59))
                day_energy_data = smart_building.get_energy_usage(
                    start_datetime, end_datetime
                )

                for energy_data in day_energy_data:
                    device_obj = Device.objects.get(id=energy_data["device_id"])
                    measurements.append(
                        EnergyDailyMeasurement(
                            device=device_obj,
                            datetime=end_datetime,
                            energy_value=energy_data.get("energy_value"),
                        )
                    )
        return measurements

    def _download_energy_data_task_tmp(self, start_date: datetime, end_date: datetime):
        serialized_building = BuildingSerializer(self._building).data
        smart_building = SmartHomeBuilding(serialized_building)

        measurements = []
    
        day_energy_data = smart_building.get_energy_usage(
            start_date, end_date
        )

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
