from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict

from .constants import EnergySource as sources
from .energy_calculators import sources_calculators
from .exchange_regressors import ExchangeEnergyRegressor
from .models import EnergyGenerator, EnergySourcesRaport, EnergyStorage
from .price_manager import PriceManager


class BuildingEnergyManager:
    _energy_sources_raport = None
    _energy_surplus_all_sources_data = None
    _exchange_energy_regressor = None
    _price_manager = None

    def __init__(self, building, sources_calculators=sources_calculators):
        self._building = building
        self._sources_calculators = sources_calculators
        self._exchange_energy_regressor = ExchangeEnergyRegressor()
        self._price_manager = PriceManager()
        self._initialize_calculators_for_energy_sources()

    def manage_energy_sources(self, energy_demand) -> Dict[str, Any]:
        self._energy_sources_raport = self._initialize_energy_sources_data()
        self._energy_surplus_all_sources_data = defaultdict(lambda: 0)

        energy_missing = self._use_energy_from_sources(energy_demand)
        self._store_remaining_energy(energy_missing)

        self._set_up_exchange(energy_demand)
        return self._energy_sources_raport, self._energy_surplus_all_sources_data

    def update_home_energy_data(self, start_date, end_date, energy_used, energy_generated, storage_measurements):
        self._datetime_from = start_date
        self._datetime_to = end_date
        self._price_manager.update_date(start_date, end_date)
        self._sources_calculators[sources.PHOTOVOLTAICS].update_energy_generated(
            energy_generated
        )
        self._sources_calculators[sources.GRID_SURPLUS].update_current_datetime(end_date)

        avaliable_photovoltaics = self._has_source(sources.PHOTOVOLTAICS)
        generation_power = 0.0
        if avaliable_photovoltaics:
            try:
                energy_generators = EnergyGenerator.objects.filter(building=self._building)
                for generator in energy_generators:
                    generation_power += generator.generation_power
            except EnergyGenerator.DoesNotExist:
                pass

        available_storage = self._has_source(sources.ENERGY_STORAGE)
        initial_storage_charge_value = 0.0
        total_storage_capacity = 0.0
        if  available_storage:
            try:
                storage_device = EnergyStorage.objects.get(building = self._building)
                total_storage_capacity = storage_device.capacity
            except EnergyStorage.DoesNotExist:
                pass
            available_storage.update_storage_params(start_date, end_date, storage_measurements)
            initial_storage_charge_value = available_storage._get_device_current_capacity(storage_device)

        available_exchange = self._has_source(sources.ENERGY_EXCHANGE)
        if available_exchange:
            available_exchange.update_current_datetime(start_date, end_date)

        initial_grid_surplus = self._sources_calculators[sources.GRID_SURPLUS]._get_current_grid_surplus()

        self._exchange_energy_regressor.update_initial_energy_data(
            {
                "end_date": end_date,
                "start_date": start_date,
                "energy_generation": energy_generated, #how much energy was generated during timestamp
                "energy_usage": abs(energy_used), #how much energy was used during timestamp
                "initial_storage_charge_value": initial_storage_charge_value,
                "initial_grid_surplus_value": initial_grid_surplus,
                "total_storage_capacity": total_storage_capacity,
                "generation_power" : generation_power,
            }
        )


    def _set_up_exchange(self, energy_usage):
        available_exchange = self._has_source(sources.ENERGY_EXCHANGE)
        if not available_exchange:
            return
        available_storage = self._has_source(sources.ENERGY_STORAGE)
        storage_charge_value = 0.0
        if  available_storage:
            storage_device = EnergyStorage.objects.get(building = self._building)
            storage_charge_value = available_storage._get_device_current_capacity(storage_device)
        energy_surplus = self._sources_calculators[sources.GRID_SURPLUS]._get_current_grid_surplus()
        public_grid_usage = self._energy_sources_raport.energy_sources[sources.PUBLIC_GRID].get("value", 0)

        self._exchange_energy_regressor.update_energy_data(
            {
                # "energy_usage": energy_usage, #how much energy was used during timestamp
                "energy_storage": storage_charge_value, #how much energy is inside storage after timestamp
                "surplus_data": energy_surplus, #how much energy is in surplus after timestamp
                "public_grid_data": public_grid_usage, #how much energy was needed from public grid during timestamp
            }
        )
        self._exchange_energy_to_buy = self._exchange_energy_regressor.decide_energy_to_buy()

        print('self._exchange_energy_to_buy: ', self._exchange_energy_to_buy)
        available_exchange.buy_exchange_energy(self._exchange_energy_to_buy)


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
                    remaining_energy = available_storage.store_energy_surplus(remaining_energy)
                    stored_energy = energy_to_store - remaining_energy
                    exchange_calc.update_remained_energy(remaining_energy)
                    self._update_energy_surpluses_data(sources.ENERGY_STORAGE, stored_energy)
                    energy_price = self._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
                    self._update_energy_sources_data(sources.ENERGY_EXCHANGE, stored_energy, energy_price)
            if self._is_energy_surplus(remaining_energy):
                exchange_ends_in = (available_exchange_energy.date_time_to - self._datetime_to).total_seconds()/60

                if  exchange_ends_in < 20 and exchange_ends_in >= 0: #ends in less than 20 minutes but hasnt ended yet
                    self._store_exchange_remaining_energy_into_grid_surplus(remaining_energy)

    def _store_remaining_energy(self, remaining_energy):
        grid_surplus = self._sources_calculators[sources.GRID_SURPLUS]
        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        if available_storage:
            if self._is_energy_surplus(remaining_energy):
                remaining_energy = self._store_photovoltaics_surplus_into_energy_storage(remaining_energy)
            
            available_exchange = self._has_source(sources.ENERGY_EXCHANGE)
            if available_exchange:
                self._store_exchange_energy()

            try:
                available_exchange_energy = available_exchange.get_current_exchange_storage()
            except AttributeError:
                available_exchange_energy = False

            if not available_exchange_energy:
                self._store_grid_surplus_into_energy_storage()

        if self._is_energy_surplus(remaining_energy):
            energy_to_store = remaining_energy
            remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)
            stored_energy = energy_to_store - remaining_energy
            self._update_energy_surpluses_data(sources.GRID_SURPLUS, stored_energy)


    def _store_photovoltaics_surplus_into_energy_storage(self, remaining_energy):
        storage_calc = self._sources_calculators.get(sources.ENERGY_STORAGE)
        energy_to_store = remaining_energy
        remaining_energy = storage_calc.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        self._update_energy_surpluses_data(sources.ENERGY_STORAGE, stored_energy)

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
        grid_surplus.calculate_energy_cover(0-stored_energy, battery_charging=True)
        energy_price = self._price_manager.get_price_by_source(grid_source)
        self._update_energy_sources_data(grid_source, stored_energy, energy_price)
        self._update_energy_surpluses_data(sources.ENERGY_STORAGE, stored_energy)

    def _store_exchange_remaining_energy_into_grid_surplus(self, remaining_energy):
        grid_surplus = self._sources_calculators.get(sources.GRID_SURPLUS)
        energy_to_store = remaining_energy
        remaining_energy = grid_surplus.store_energy_surplus(remaining_energy)
        stored_energy = energy_to_store - remaining_energy
        self._update_energy_surpluses_data(sources.GRID_SURPLUS, stored_energy)

    def _update_energy_sources_data(self, source, value, price):
        grosze = Decimal("0.01")
        full_price = price * float(value)
        self._energy_sources_raport.energy_sources[source]["value"]+=value
        self._energy_sources_raport.energy_sources[source]["price"]+=Decimal(full_price).quantize(grosze, ROUND_HALF_UP)


    def _update_energy_surpluses_data(self, source, value):
        self._energy_surplus_all_sources_data[source] += value


    def _initialize_energy_sources_data(self):
        grosze = Decimal("0.01")
        energy_sources_data = {}
        for source in self._sources_calculators.keys():
            energy_sources_data[source] = {
                "value": 0,
                "price": Decimal(0).quantize(grosze, ROUND_HALF_UP),
            }
        raport = EnergySourcesRaport(
                    building=self._building,
                    date_time_from=self._datetime_from,
                    date_time_to=self._datetime_to,
                    energy_sources=energy_sources_data,
                )
        return raport

    def _initialize_calculators_for_energy_sources(self):
        for source, calc in self._sources_calculators.items():
            self._sources_calculators[source] = calc(self._building)
