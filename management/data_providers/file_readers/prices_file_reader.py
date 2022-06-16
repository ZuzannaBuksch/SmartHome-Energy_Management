from .json_file_reader import JsonFileReader

class PricesFileReader(JsonFileReader):
    DATA_FILENAME = "data_json/energy_market.json"
