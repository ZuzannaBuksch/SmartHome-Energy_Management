from datetime import datetime
from .file_readers import PricesFileReader

class ExchangePricesDataProvider:
    def __init__(self):
        self._file_reader = PricesFileReader()

    def get_data(self, date_time: datetime):
        prices = self._read_prices_file()
        current_price = prices.get(date_time, 0.69)
        return current_price


# {  "2022-05-09 10:00:00" : 0.45,
#   "2022-05-09 10:00:00" : 0.45,
#   "2022-05-09 10:00:00" : 0.45 }
