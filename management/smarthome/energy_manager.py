
from typing import List
from .models import EnergyDailyMeasurement, Device
from .serializers import BuildingSerializer
from services.smart_home import SmartHomeBuilding
from datetime import datetime, time, timedelta
from .price_classifier import PriceClassifier

class BuildingEnergyManager:
    def __init__(self, building):
        self._building = building

    def manage_building_energy(self, start_date: datetime, end_date: datetime):
        measurements = self._download_energy_data_task(start_date, end_date)

        measurements = PriceClassifier().decide_energy_prices(measurements)
        
        
        # measurements = self._bulk_create_daily_measurements(measurements)
        return measurements



    def _bulk_create_daily_measurements(self, measurements: List[EnergyDailyMeasurement]):
        return EnergyDailyMeasurement.objects.bulk_create(measurements, ignore_conflicts=True)

    def _download_energy_data_task(self, start_date: datetime, end_date: datetime):
        serialized_building = BuildingSerializer(self._building).data
        smart_building = SmartHomeBuilding(serialized_building)

        measurements = []
        days = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]
        hours = [hour for hour in range(0,24)]
        for day in days:
            for hour in hours:
                start_datetime = datetime.combine(day, time(hour,0,0))
                end_datetime = datetime.combine(day, time(hour,59,59))
                day_energy_data = smart_building.get_energy(start_datetime, end_datetime)
                
                for energy_data in day_energy_data:
                    device_obj = Device.objects.get(id=energy_data["device_id"])
                    measurements.append(EnergyDailyMeasurement(
                        device=device_obj, 
                        datetime=end_datetime, 
                        energy_value=energy_data.get("energy_value")
                        ))
        return measurements
