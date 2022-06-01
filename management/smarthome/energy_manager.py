from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict
from collections import OrderedDict

from .constants import EnergySource as sources
from .energy_calculators import sources_calculators
from .energy_calculators.calculators_sources import get_by_value
from .price_manager import PriceManager


class BuildingEnergyManager:
    _energy_sources_data = None
    _energy_surplus_data = None

    def __init__(self, building, sources_calculators=sources_calculators):
        self._building = building
        self._sources_calculators = sources_calculators
        self._initialize_calculators_for_energy_sources()

    def manage_energy_sources(self, energy_demand) -> Dict[str, Any]:
        self._energy_sources_data = {}
        self._energy_surplus_data = {}

        energy_missing = self._use_energy_from_sources(energy_demand)
        self._store_remaining_energy(energy_missing)

        return self._energy_sources_data, self._energy_surplus_data

    def has_source(self, source):
        return self._sources_calculators.get(source)

    def update_storage_energy(self, measurements, raports):
        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        if  available_storage:
            available_storage.update_energy_states_and_usages(
                measurements, raports
            )

    def update_dates_range(self, start_date, end_date):
        self._sources_calculators[sources.GRID_SURPLUS].update_datetime(end_date)

        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        if  available_storage:
            available_storage.update_dates_range(start_date, end_date)

    def update_energy_generated(self, energy_generated):
        self._sources_calculators[sources.PHOTOVOLTAICS].update_energy_generated(
            energy_generated
        )

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

    def _store_remaining_energy(self, remaining_energy):
        available_sources = [self._sources_calculators[sources.GRID_SURPLUS]]
        available_storage = self._sources_calculators.get(sources.ENERGY_STORAGE)
        if available_storage:
            available_sources.insert(0,available_storage)
        
        for source in available_sources:
            stored_energy = 0
            is_energy_surplus = remaining_energy > 0
            if is_energy_surplus:
                energy_to_store = remaining_energy
                remaining_energy = source.store_energy_surplus(remaining_energy)
                stored_energy = energy_to_store - remaining_energy
            self._energy_surplus_data[get_by_value(source.__class__)] = stored_energy


    def _update_energy_sources_data(self, source, value, price, sources={}):
        grosze = Decimal("0.01")
        full_price = price * float(value)
        self._energy_sources_data[source] = {
            "value": value,
            "price": Decimal(full_price).quantize(grosze, ROUND_HALF_UP),
        }

    def _initialize_calculators_for_energy_sources(self):
        for source, calc in self._sources_calculators.items():
            self._sources_calculators[source] = calc(self._building)
