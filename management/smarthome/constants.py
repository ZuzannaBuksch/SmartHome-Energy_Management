from enum import Enum

class EnergySource(Enum):
    PHOTOVOLTAICS = "photovoltaics"
    PUBLIC_GRID = "public grid"
    GRID_SURPLUS = "grid surplus"
    ENERGY_STORAGE = "energy storage"
