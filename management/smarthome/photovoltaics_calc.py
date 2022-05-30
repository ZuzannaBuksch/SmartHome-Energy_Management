class PhotovoltaicsEnergyCalculator:

    def calculate_photovoltaics_cover(self, energy_generated, energy_demand):
        photovoltaics_energy_used = min(energy_demand, energy_generated)
        photovoltaics_cover = energy_generated - energy_demand
        return photovoltaics_energy_used, photovoltaics_cover #informacja czy energii z nadywzki wystarczyło na pokrycie wszystkiego
