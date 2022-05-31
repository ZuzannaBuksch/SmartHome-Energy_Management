from ..constants import EnergySource as sources
from . import PhotovoltaicsEnergyCalculator, GridSurplusEnergyCalculator, PublicGridEnergyCalculator, EnergyStorageCalculator

sources_calculators = {
                sources.PHOTOVOLTAICS: PhotovoltaicsEnergyCalculator,
                sources.GRID_SURPLUS: GridSurplusEnergyCalculator,
                sources.ENERGY_STORAGE: EnergyStorageCalculator,
                sources.PUBLIC_GRID: PublicGridEnergyCalculator,
            }
