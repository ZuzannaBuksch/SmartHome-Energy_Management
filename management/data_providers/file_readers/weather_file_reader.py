from .json_file_reader import JsonFileReader


class WeatherFileReader(JsonFileReader):
    DATA_FILENAME = "data_json/weather.json"
