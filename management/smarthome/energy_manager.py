from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from services.smart_home import SmartHomeBuilding

from .models import Device, EnergyDailyMeasurement, EnergyGenerator, EnergyReceiver, EnergySourcesRaport, EnergySurplusRaport
from .price_classifier import PriceClassifier
from .serializers import BuildingSerializer

PHOTOVOLTAICS = "photovoltaics"
PUBLIC_GRID = "public grid"
GRID_SURPLUS = "grid surplus"

class GridSurplusEnergyCalculator:
        def __init__(self, building, date_time):
            self._building = building
            self._date_time = date_time
        
        def create_new_grid_surplus(self, type_, value):
            EnergySurplusRaport.objects.create(usage_type=type_, value=value, building=self._building, date_time = self._date_time)

        def _get_current_grid_surplus(self): #TODO
            try:
                return EnergySurplusRaport.objects.filter(building=self._building).latest('date_time').value
            except EnergySurplusRaport.DoesNotExist:
                return 0

        def calculate_grid_surplus_cover(self, energy_demand):
            current_surplus = self._get_current_grid_surplus()
            surplus_energy_used = 0
            if current_surplus > 0:
                surplus_energy_used = min(current_surplus, abs(energy_demand))
                self.create_new_grid_surplus(EnergySurplusRaport.DEVICES_POWERING, surplus_energy_used)
            surplus_cover = current_surplus - abs(energy_demand)
            return surplus_energy_used, surplus_cover #informacja czy energii z nadywzki wystarczyło na pokrycie wszystkiego

class BuildingEnergyManager:
    _PUBLIC_GRID_PRICE = 0.68 #PLN

    def __init__(self, building):
        self._building = building

    def manage_building_energy(self, start_date: datetime, end_date: datetime):
        measurements = self._download_energy_data_task_tmp(start_date, end_date)
        energy_generated = self._calculate_energy_sum(self._get_measurements_by_type(measurements, EnergyGenerator.__name__))
        energy_demand = self._calculate_energy_sum(self._get_measurements_by_type(measurements, EnergyReceiver.__name__))

        grid_surplus_calc = GridSurplusEnergyCalculator(self._building, end_date)
        
        energy_surplus = energy_generated - energy_demand #pokrycie zapotrzebowania przez fotowoltaike
        is_enough_energy = energy_surplus >= 0

        if is_enough_energy:
            grid_surplus_calc.create_new_grid_surplus(EnergySurplusRaport.TRANSFER, energy_surplus)
            sources = self._update_energy_sources(PHOTOVOLTAICS, energy_demand, 0, {})
        else:
            self._update_energy_sources(PHOTOVOLTAICS, energy_generated, 0)
            grid_surplus_used, grid_surplus_cover = grid_surplus_calc.calculate_grid_surplus_cover(abs(energy_surplus))
            self._update_energy_sources(GRID_SURPLUS, grid_surplus_used, 0) #TODO
            sources = self._update_energy_sources(PUBLIC_GRID, abs(grid_surplus_cover), 0.68)

        sources_raport = EnergySourcesRaport(building=self._building, date_time_from = start_date, date_time_to=end_date, energy_sources=sources)
        # measurements = self._bulk_create_daily_measurements(measurements)
        return measurements, sources_raport
     
    def _update_energy_sources(self, source, value, price, sources={}):
        grosze = Decimal('0.01')
        full_price = price*value
        sources[source] = {
            "value": value,
            "price": Decimal(full_price).quantize(grosze, ROUND_HALF_UP)
        }
        return sources

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
