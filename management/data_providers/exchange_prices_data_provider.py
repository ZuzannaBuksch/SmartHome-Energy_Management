import pandas as pd
from datetime import datetime, timedelta
from .file_readers import PricesFileReader

class ExchangePricesDataProvider:
    def __init__(self):
        self._file_reader = PricesFileReader()

    def get_data(self, start_datetime: datetime, end_datetime: datetime):
        prices_data = self._file_reader.read_file()
        
        to_date = lambda str_date: datetime.strptime(str_date,"%Y-%m-%d %H:%M:%S")
        prices_cols = [[to_date(k), v] for item in prices_data for k, v in item.items()]
        prices_df = pd.DataFrame(prices_cols, columns=["datetime", "price"])

        return prices_df[prices_df.datetime.between(start_datetime, end_datetime)]
