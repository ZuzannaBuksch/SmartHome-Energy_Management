import pandas as pd
from datetime import datetime, timedelta
from .file_readers import WeatherFileReader

class WeatherDataProvider:
    def __init__(self):
        self._file_reader = WeatherFileReader()

    def get_data(self, date_time: datetime, days_range=10):
        weather_data = self._file_reader.read_file()
        
        to_date = lambda str_date: datetime.strptime(str_date,"%Y-%m-%d %H:%M:%S")
        weather_cols = [[to_date(k), v["real"]["solar_radiation"], v["forecast"]["solar_radiation"]] for k, v in weather_data.items()]
        weather_df = pd.DataFrame(weather_cols, columns=["datetime", "real", "forecast"])
        
        earliest_datetime = date_time - timedelta(days=days_range)
        return weather_df[weather_df.datetime.between(earliest_datetime, date_time)]



