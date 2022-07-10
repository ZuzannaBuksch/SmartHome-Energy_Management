from .constants import EnergySource as sources
from data_providers.exchange_prices_data_provider import ExchangePricesDataProvider

class PriceManager:
    def __init__(self):
        self._public_grid_price = 0.68 #PLN
        self._photovoltaics_price = 0.0
        self._grid_surplus_price = 0.0
        self._energy_storage_price = 0.0
        self._energy_exchange_price = None

    def update_date(self, start_date, end_date):
        exchange_prices = ExchangePricesDataProvider().get_data(start_date, end_date)
        self._energy_exchange_price = exchange_prices.iloc[exchange_prices["datetime"].argmax()]["price"]

    def get_price_by_source(self, energy_source):
        return {
            sources.PHOTOVOLTAICS: self._photovoltaics_price,
            sources.GRID_SURPLUS: self._grid_surplus_price,
            sources.ENERGY_STORAGE: self._energy_storage_price,
            sources.PUBLIC_GRID: self._public_grid_price,
            sources.ENERGY_EXCHANGE: self._energy_exchange_price,
        }.get(energy_source)
