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
