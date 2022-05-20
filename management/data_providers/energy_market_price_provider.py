import json
from datetime import datetime

PRICES_JSON_FILE = None


class EnergyMarketPriceProvider:
    def get_price(self, date_time: datetime):
        prices = self._read_prices_file()
        current_price = prices.get(date_time, 0.69)
        return current_price

    def _read_prices_file(self):
        try:
            with open(PRICES_JSON_FILE, "r") as f:
                prices = json.load(f)
        except TypeError:
            prices = {}
        return prices


# {  "2022-05-09 10:00:00" : 0.45,
#   "2022-05-09 10:00:00" : 0.45,
#   "2022-05-09 10:00:00" : 0.45 }
