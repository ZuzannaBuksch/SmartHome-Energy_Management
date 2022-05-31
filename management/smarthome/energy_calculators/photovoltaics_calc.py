from .base_calc import BaseEnergyCalculator, is_energy_needed


class PhotovoltaicsEnergyCalculator(BaseEnergyCalculator):
    _energy_generated = 0

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand):
        energy_demand = abs(energy_demand)
        photovoltaics_energy_used = min(energy_demand, self._energy_generated)
        photovoltaics_cover = self._energy_generated - energy_demand
        return (
            photovoltaics_energy_used,
            photovoltaics_cover,
        )  # informacja czy energii z nadywzki wystarczyło na pokrycie wszystkiego

    def update_energy_generated(self, energy):
        self._energy_generated = energy
