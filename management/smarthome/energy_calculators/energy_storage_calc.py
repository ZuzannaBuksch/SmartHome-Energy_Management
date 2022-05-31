from .base_calc import BaseEnergyCalculator, is_energy_needed

class EnergyStorageCalculator(BaseEnergyCalculator):
    _current_capacity = None
        
    def update_current_capacity(self, capacity):
            self._current_capcity = capacity
    
    def put_energy_to_storage(self, energy, *args, **kwargs):
            #_calculate_charge_time
            #create new raport in simulation
        pass
    
    @is_energy_needed
    def calculate_energy_cover(self, energy_demand):
        storage_energy_used, storage_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        if self._current_capacity > 0:
            storage_energy_used = min(self._current_capacity, energy_demand)
            #_calculate_charge_time
            #create new raport in simulation
            storage_cover = self._current_capacity - energy_demand
        return storage_energy_used, storage_cover #informacja czy energii z magazynu wystarczyło na pokrycie wszystkiego
            
    def _calculate_charge_time(self, *args, **kwargs):
            return 0.48
        