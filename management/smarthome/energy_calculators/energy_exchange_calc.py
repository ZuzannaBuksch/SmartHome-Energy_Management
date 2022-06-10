from ..models import ExchangeEnergyStorageRaport
from .base_calc import BaseEnergyCalculator, is_energy_needed


class EnergyExchangeCalculator(BaseEnergyCalculator):
    _date_time = None

    def update_current_datetime(self, date_time):
        self._date_time = date_time
        self._exchange_storage = self.get_current_exchange_storage()

    def update_remained_energy(self, remaining_energy):
        self._exchange_storage.remained_value = remaining_energy
        self._exchange_storage.save(update_fields=["remained_value"])

    def update_remained_energy(self, remaining_energy):
        self._exchange_storage.remained_value = remaining_energy
        self._exchange_storage.save(update_fields=["remained_value"])

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand):
        surplus_energy_used, surplus_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        if self._exchange_storage:
            stored_energy = self._exchange_storage.remained_value
            if stored_energy>0:
                surplus_energy_used = min(stored_energy, energy_demand)
                remained_energy = round(self._exchange_storage.remained_value - surplus_energy_used, 5)
                self.update_remained_energy(remained_energy)
                
            surplus_cover = surplus_energy_used - energy_demand
        return surplus_energy_used, surplus_cover

    def get_current_exchange_storage(self):
        try:
            raport = (
                ExchangeEnergyStorageRaport.objects.filter(building=self._building)
                .latest("date_time_to")
            )
        except ExchangeEnergyStorageRaport.DoesNotExist:
            return
        if raport.date_time_to >= self._date_time and raport.remained_value>0: #TODO not sure about time_to 
            return raport
