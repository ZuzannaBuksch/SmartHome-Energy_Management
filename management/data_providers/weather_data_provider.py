import pandas as pd
from datetime import datetime
from .file_readers import WeatherFileReader

class WeatherDataProvider:
    def __init__(self):
        self._file_reader = WeatherFileReader()

    def get_data(self, start_datetime: datetime, end_datetime: datetime = None):
        weather_data = self._file_reader.read_file()
        
        to_date = lambda str_date: datetime.strptime(str_date,"%Y-%m-%d %H:%M:%S")
        weather_cols = [[to_date(k), v["real"]["solar_radiation"], v["forecast"]["solar_radiation"]] for k, v in weather_data.items()]
        weather_df = pd.DataFrame(weather_cols, columns=["datetime_to", "real", "forecast"])


        return weather_df[weather_df.datetime_to.between(start_datetime, end_datetime)]



