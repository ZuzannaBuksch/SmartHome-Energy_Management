from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict
from collections import defaultdict

from .constants import EnergySource as sources
from .energy_calculators import sources_calculators, ExchangeEnergyClassifier
from .energy_calculators.calculators_sources import get_by_value
from .price_manager import PriceManager


class BuildingEnergyManager:
    _energy_sources_data = None
    _energy_surplus_data = None
    _ExchangeEnergyClassifier = None

    def __init__(self, building, sources_calculators=sources_calculators):
        self._building = building
        self._sources_calculators = sources_calculators
        self._ExchangeEnergyClassifier = ExchangeEnergyClassifier()
        self._initialize_calculators_for_energy_sources()

    def manage_energy_sources(self, energy_demand) -> Dict[str, Any]:
        self._will_buy_exchange_energy = self._ExchangeEnergyClassifier.decide_if_buy()
        self._energy_sources_data = {}
        self._energy_surplus_data = defaultdict(lambda: 0)

        energy_missing = self._use_energy_from_sources(energy_demand)
        self._store_remaining_energy(energy_missing)

        return self._energy_sources_data, self._energy_surplus_data

    def update_home_energy_data(self, start_date, end_date, energy_generated, storage_measurements, storage_usage_raports):
        self._datetime_from = start_date
        self._datetime_to = end_date
        self._sources_calculators[sources.PHOTOVOLTAICS].update_energy_generated(
            energy_generated
        )
        self._sources_calculators[sources.GRID_SURPLUS].update_current_datetime(end_date)

        available_storage = self._has_source(sources.ENERGY_STORAGE)
        if  available_storage:
            available_storage.update_storage_params(start_date, end_date, storage_measurements, storage_usage_raports)

        available_exchange = self._has_source(sources.ENERGY_EXCHANGE)
        if available_exchange:
            available_exchange.update_current_datetime(end_date)

    def _use_energy_from_sources(self, energy_demand):
        energy_missing = energy_demand
        pm = PriceManager()
        for source, energy_calc in self._sources_calculators.items():
            energy_price = pm.get_price_by_source(source)
            energy_used, energy_missing = energy_calc.calculate_energy_cover(
                energy_missing
            )
            self._update_energy_sources_data(source, energy_used, energy_price)
        return energy_missing

    def _is_energy_surplus(self, energy):
        return energy > 0
        
    def _has_source(self, source):
        return self._sources_calculators.get(source)  


    def _store_exchange_energy(self):
        exchange_calc = self._sources_calculators[sources.ENERGY_EXCHANGE]
        available_exchange_energy = exchange_calc.get_current_exchange_storage()
        if available_exchange_energy:
            remaining_energy = available_exchange_energy.remained_value

            if self._is_energy_surplus(remaining_energy):
                available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
                if available_storage:
                    energy_to_store = remaining_energy
                    remaining_energy = available_storage.store_energy_surplus(remaining_energy)
                    stored_energy = energy_to_store - remaining_energy
                    self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy
                    available_exchange_energy.remained_energy = remaining_energy
            
            if self._is_energy_surplus(remaining_energy):
                if available_exchange_energy.date_time_to <= self._datetime_to:
                    self._store_exchange_remaining_energy_into_grid_surplus(remaining_energy)

    def _store_remaining_energy(self, remaining_energy):
        grid_surplus = self._sources_calculators[sources.GRID_SURPLUS]

        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        if available_storage:
            if self._is_energy_surplus(remaining_energy):
                remaining_energy = self._store_photovoltaics_surplus_into_energy_storage(remaining_energy)
            if self._has_source(sources.ENERGY_EXCHANGE):
                self._store_exchange_energy()
            if not self._will_buy_exchange_energy:
                self._store_grid_surplus_into_energy_storage()

        if self._is_energy_surplus(remaining_energy):
            remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)


    def _store_photovoltaics_surplus_into_energy_storage(self, remaining_energy):
        storage_calc = self._sources_calculators.get(sources.ENERGY_STORAGE)
        energy_to_store = remaining_energy
        remaining_energy = storage_calc.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy
        return remaining_energy 


    def _store_grid_surplus_into_energy_storage(self):
        grid_surplus = self._sources_calculators[sources.GRID_SURPLUS]
        grid_surplus_val = grid_surplus._get_current_grid_surplus()
        storage_calc = self._sources_calculators.get(sources.ENERGY_STORAGE)
        remaining_grid_energy = storage_calc.store_energy_surplus(grid_surplus_val)
        stored_energy = grid_surplus_val - remaining_grid_energy
        grid_surplus.calculate_energy_cover(stored_energy) #TODO: test raport from db
        self._energy_sources_data[sources.GRID_SURPLUS]['value'] += stored_energy
        self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy

    def _store_exchange_remaining_energy_into_grid_surplus(self, remaining_energy):
        grid_surplus = self._sources_calculators.get(sources.GRID_SURPLUS)
        energy_to_store = remaining_energy
        remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        self._energy_surplus_data[sources.GRID_SURPLUS] += stored_energy    

    def _update_energy_sources_data(self, source, value, price):
        grosze = Decimal("0.01")
        full_price = price * float(value)
        self._energy_sources_data[source] = {
            "value": value,
            "price": Decimal(full_price).quantize(grosze, ROUND_HALF_UP),
        }

    def _initialize_calculators_for_energy_sources(self):
        for source, calc in self._sources_calculators.items():
            self._sources_calculators[source] = calc(self._building)
