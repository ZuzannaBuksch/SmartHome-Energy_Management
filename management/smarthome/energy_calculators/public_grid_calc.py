from .base_calc import BaseEnergyCalculator, is_energy_needed

class PublicGridEnergyCalculator(BaseEnergyCalculator):

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand):
        return abs(energy_demand), 0
