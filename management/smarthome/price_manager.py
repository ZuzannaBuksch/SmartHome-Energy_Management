from .constants import EnergySource as sources

class PriceManager:
    def __init__(self):
        self._public_grid_price = 0.68 #PLN
        self._photovoltaics_price = 0.0
        self._grid_surplus_price = 0.0
        self._energy_storage_price = 0.0

    def get_price_by_source(self, energy_source):
        return {
            sources.PHOTOVOLTAICS: self._photovoltaics_price,
            sources.GRID_SURPLUS: self._grid_surplus_price,
            sources.ENERGY_STORAGE: self._energy_storage_price,
            sources.PUBLIC_GRID: self._public_grid_price,
        }.get(energy_source)
