from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict

from .constants import EnergySource as sources
from .energy_calculators import sources_calculators
from .price_manager import PriceManager


class BuildingEnergyManager:
    def __init__(self, building, sources_calculators=sources_calculators):
        self._building = building
        self._sources_calculators = sources_calculators
        self._initialize_calculators_for_energy_sources()

    def manage_energy_sources(
        self, end_date: datetime, energy_demand: float, energy_generated: float
    ) -> Dict[str, Any]:
        self._energy_sources_data = {}
        self._update_energy_generated(energy_generated)
        self._update_datetime(end_date)

        energy_missing = self._use_energy_from_sources(energy_demand)
        self._store_remaining_energy(energy_missing)

        return self._energy_sources_data

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
        is_energy_surplus = remaining_energy > 0
        if is_energy_surplus:
            self._sources_calculators[sources.GRID_SURPLUS].put_energy_to_grid_surplus(
                remaining_energy
            )

    def _update_datetime(self, date_time):
        self._sources_calculators[sources.GRID_SURPLUS].update_datetime(date_time)

    def _update_energy_generated(self, energy_generated):
        self._sources_calculators[sources.PHOTOVOLTAICS].update_energy_generated(
            energy_generated
        )

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
