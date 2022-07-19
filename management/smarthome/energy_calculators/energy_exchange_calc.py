from datetime import timedelta

from ..constants import EnergySource as sources
from ..models import ExchangeEnergyStorageRaport
from ..price_manager import PriceManager
from .base_calc import BaseEnergyCalculator, is_energy_needed


class EnergyExchangeCalculator(BaseEnergyCalculator):
    _date_time_from = None
    _date_time_to = None

    def update_current_datetime(self, date_time_from, date_time_to):
        self._date_time_from = date_time_from
        self._date_time_to = date_time_to
        self._exchange_storage = self.get_current_exchange_storage()

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

    def buy_exchange_energy(self, amount):
        if float(amount)<=0:
            return
        date_time_from = self._date_time_to+timedelta(hours=1, minutes=59, seconds=59)
        date_time_to = date_time_from+timedelta(hours=1)
        pm = PriceManager()
        pm.update_date(self._date_time_from, self._date_time_to)
        price = pm.get_price_by_source(sources.ENERGY_EXCHANGE)
        ExchangeEnergyStorageRaport.objects.create(
            building = self._building,
            total_value = amount,
            remained_value = amount,
            purchase_price = price,
            date_time_from = date_time_from,
            date_time_to = date_time_to
        )

    def get_current_exchange_storage(self):
        try:
            raport = (
                ExchangeEnergyStorageRaport.objects.filter(building=self._building)
                .latest("date_time_to")
            )
        except ExchangeEnergyStorageRaport.DoesNotExist:
            return
        exchange_range_gt_current_timestamp = raport.date_time_from <= self._date_time_from and raport.date_time_to >= self._date_time_to
        exchange_started_after_start = raport.date_time_from >= self._date_time_from and raport.date_time_from <= self._date_time_to
        exchange_ended_before_end = raport.date_time_to >= self._date_time_from and raport.date_time_to < self._date_time_to
        if  (exchange_range_gt_current_timestamp or exchange_started_after_start or exchange_ended_before_end) and raport.remained_value>0:
            return raport
