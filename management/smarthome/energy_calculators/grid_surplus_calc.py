from ..models import EnergySurplusRaport
from .base_calc import BaseEnergyCalculator, is_energy_needed
from django.db.utils import IntegrityError

class GridSurplusEnergyCalculator(BaseEnergyCalculator):
    _date_time = None

    def update_current_datetime(self, value):
        self._date_time = value

    def store_energy_surplus(self, energy):
        self._create_new_grid_surplus(EnergySurplusRaport.TRANSFER, abs(energy))
        return 0

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand, battery_charging=False):
        surplus_energy_used, surplus_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        current_surplus = self._get_current_grid_surplus()

        if current_surplus > 0:
            surplus_energy_used = min(current_surplus, energy_demand)
            usage = EnergySurplusRaport.BATTERY_CHARGING if battery_charging else EnergySurplusRaport.DEVICES_POWERING
            self._create_new_grid_surplus(usage, surplus_energy_used)
        surplus_cover = surplus_energy_used - energy_demand
        return (
            surplus_energy_used,
            surplus_cover,
        )  # informacja czy energii z nadywzki wystarczyło na pokrycie wszystkiego

    def _get_current_grid_surplus(self):
        try:
            return (
                EnergySurplusRaport.objects.filter(building=self._building)
                .last()
                .value
            )
        except AttributeError:
            return 0

    def _create_new_grid_surplus(self, type_, value):
        if value>0:
            try:
                x, _ =EnergySurplusRaport.objects.get_or_create(
                    usage_type=type_,
                    value=value,
                    building=self._building,
                    date_time=self._date_time,
                )

            except IntegrityError:
                pass
