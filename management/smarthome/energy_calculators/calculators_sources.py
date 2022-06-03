from collections import OrderedDict
from ..constants import EnergySource as sources
from . import PhotovoltaicsEnergyCalculator, GridSurplusEnergyCalculator, PublicGridEnergyCalculator, EnergyStorageCalculator
from .energy_exchange_calc import EnergyExchangeCalculator

sources_calculators = OrderedDict([
                (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
                (sources.ENERGY_EXCHANGE, EnergyExchangeCalculator),
                (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
                (sources.ENERGY_STORAGE, EnergyStorageCalculator),
                (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
                ])


def get_by_value(value):
    for k, v in sources_calculators.items():
        if v==value:
            return k
