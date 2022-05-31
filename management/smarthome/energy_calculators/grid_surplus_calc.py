from ..models import EnergySurplusRaport
from .base_calc import BaseEnergyCalculator, is_energy_needed


class GridSurplusEnergyCalculator(BaseEnergyCalculator):
    _date_time = None

    def update_datetime(self, value):
        self._date_time = value

    def put_energy_to_grid_surplus(self, energy):
        self._create_new_grid_surplus(EnergySurplusRaport.TRANSFER, abs(energy))

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand):
        surplus_energy_used, surplus_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        current_surplus = self._get_current_grid_surplus()
        if current_surplus > 0:
            surplus_energy_used = min(current_surplus, energy_demand)
            self._create_new_grid_surplus(
                EnergySurplusRaport.DEVICES_POWERING, surplus_energy_used
            )
        surplus_cover = current_surplus - energy_demand
        return (
            surplus_energy_used,
            surplus_cover,
        )  # informacja czy energii z nadywzki wystarczyło na pokrycie wszystkiego

    def _get_current_grid_surplus(self):
        try:
            return (
                EnergySurplusRaport.objects.filter(building=self._building)
                .latest("date_time")
                .value
            )
        except EnergySurplusRaport.DoesNotExist:
            return 0

    def _create_new_grid_surplus(self, type_, value):
        EnergySurplusRaport.objects.create(
            usage_type=type_,
            value=value,
            building=self._building,
            date_time=self._date_time,
        )
