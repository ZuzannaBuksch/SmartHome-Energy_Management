from collections import defaultdict
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict

from .constants import EnergySource as sources
from .energy_calculators import ExchangeEnergyClassifier, sources_calculators
from .energy_calculators.calculators_sources import get_by_value
from .price_manager import PriceManager


class BuildingEnergyManager:
    _energy_sources_data = None
    _energy_surplus_data = None
    _exchange_energy_classifier = None
    _price_manager = None

    def __init__(self, building, sources_calculators=sources_calculators):
        self._building = building
        self._sources_calculators = sources_calculators
        self._exchange_energy_classifier = ExchangeEnergyClassifier()
        self._price_manager = PriceManager()
        self._initialize_calculators_for_energy_sources()

    def manage_energy_sources(self, energy_demand) -> Dict[str, Any]:
        self._will_buy_exchange_energy = self._exchange_energy_classifier.decide_if_buy()
        self._energy_sources_data = self._initialize_energy_sources_data()
        self._energy_surplus_data = defaultdict(lambda: 0)
        print("\n-----\n")
        print("using part with energy missing : ", energy_demand)

        energy_missing = self._use_energy_from_sources(energy_demand)
        print("storing part with energy missing : ", energy_missing)
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
            available_exchange.update_current_datetime(start_date, end_date)

    def _use_energy_from_sources(self, energy_demand):
        energy_missing = energy_demand
        for source, energy_calc in self._sources_calculators.items():
            energy_price = self._price_manager.get_price_by_source(source)
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
                    print(f"wanting to store remaining={remaining_energy} from exchange into storage")
                    remaining_energy = available_storage.store_energy_surplus(remaining_energy)
                    print(f"stored {energy_to_store} - {remaining_energy} = {energy_to_store-remaining_energy}")
                    stored_energy = energy_to_store - remaining_energy
                    exchange_calc.update_remained_energy(remaining_energy)
                    self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy
                    energy_price = self._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
                    self._update_energy_sources_data(sources.ENERGY_EXCHANGE, stored_energy, energy_price)
            if self._is_energy_surplus(remaining_energy):
                exchange_ends_in = (available_exchange_energy.date_time_to - self._datetime_to).total_seconds()/60
                print("exchange ends in ", exchange_ends_in)
                if  exchange_ends_in < 20 and exchange_ends_in >= 0: #ends in less than 20 minutes but hasnt ended yet
                    self._store_exchange_remaining_energy_into_grid_surplus(remaining_energy)

    def _store_remaining_energy(self, remaining_energy):
        grid_surplus = self._sources_calculators[sources.GRID_SURPLUS]

        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        print("in storing part remaining is ", remaining_energy, "and storage is ", available_storage)
        if available_storage:
            print("\nhirki")
            print(available_storage._storage_devices_data)
            if self._is_energy_surplus(remaining_energy):
                print("remaining energy before store ", remaining_energy)
                start = remaining_energy
                remaining_energy = self._store_photovoltaics_surplus_into_energy_storage(remaining_energy)
                print("remaining energy after store ", remaining_energy)
                print("it means we put there  ", start - remaining_energy)
                
            if self._has_source(sources.ENERGY_EXCHANGE):
                self._store_exchange_energy()
            if not self._will_buy_exchange_energy:
                self._store_grid_surplus_into_energy_storage()

        if self._is_energy_surplus(remaining_energy):
            print("after handling storage, we still have ", remaining_energy, " to store")
            energy_to_store = remaining_energy
            remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)
            print("and after transfering to grid surplus we have ", remaining_energy)
            stored_energy = energy_to_store - remaining_energy
            print("which means we stored ", stored_energy)
            self._energy_surplus_data[sources.GRID_SURPLUS] += stored_energy


    def _store_photovoltaics_surplus_into_energy_storage(self, remaining_energy):
        storage_calc = self._sources_calculators.get(sources.ENERGY_STORAGE)
        energy_to_store = remaining_energy
        remaining_energy = storage_calc.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy
        energy_price = self._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
        self._update_energy_sources_data(sources.PHOTOVOLTAICS, stored_energy, energy_price)
        return remaining_energy 


    def _store_grid_surplus_into_energy_storage(self):
        grid_source = sources.GRID_SURPLUS
        grid_surplus = self._sources_calculators[grid_source]
        grid_surplus_val = grid_surplus._get_current_grid_surplus()
        if grid_surplus_val <= 0:
            return
        storage_calc = self._sources_calculators.get(sources.ENERGY_STORAGE)
        remaining_grid_energy = storage_calc.store_energy_surplus(grid_surplus_val)
        stored_energy = grid_surplus_val - remaining_grid_energy
        grid_surplus.calculate_energy_cover(0-stored_energy)
        energy_price = self._price_manager.get_price_by_source(grid_source)
        self._update_energy_sources_data(grid_source, stored_energy, energy_price)
        self._energy_surplus_data[sources.ENERGY_STORAGE] += stored_energy

    def _store_exchange_remaining_energy_into_grid_surplus(self, remaining_energy):
        grid_surplus = self._sources_calculators.get(sources.GRID_SURPLUS)
        energy_to_store = remaining_energy
        remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        print(f"before storing exchange surplus={stored_energy} in grid surplus grid_surplus is {self._energy_surplus_data[sources.GRID_SURPLUS]}")
        self._energy_surplus_data[sources.GRID_SURPLUS] += stored_energy
        print(f"after storing exchange surplus={stored_energy} in grid surplus grid_surplus is {self._energy_surplus_data[sources.GRID_SURPLUS]}")

    def _update_energy_sources_data(self, source, value, price):
        grosze = Decimal("0.01")
        full_price = price * float(value)
        self._energy_sources_data[source]["value"]+=value
        self._energy_sources_data[source]["price"]+=Decimal(full_price).quantize(grosze, ROUND_HALF_UP)

    def _initialize_energy_sources_data(self):
        grosze = Decimal("0.01")
        energy_sources_data = {}
        for source in self._sources_calculators.keys():
            energy_sources_data[source] = {
                "value": 0,
                "price": Decimal(0).quantize(grosze, ROUND_HALF_UP),
            }
        return energy_sources_data

    def _initialize_calculators_for_energy_sources(self):
        for source, calc in self._sources_calculators.items():
            self._sources_calculators[source] = calc(self._building)
