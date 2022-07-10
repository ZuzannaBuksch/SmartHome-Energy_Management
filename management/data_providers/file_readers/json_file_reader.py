import json
import functools

class JsonFileReader:
    DATA_FILENAME = None

    @functools.lru_cache
    def read_file(self):
        try:
            with open(self.DATA_FILENAME, "r") as f:
                data = json.load(f)
        except TypeError:
            data = {}
        return data
