from .json_file_reader import JsonFileReader


class BuildingFileReader(JsonFileReader):

    def __init__(self, filename):
        self.DATA_FILENAME = filename
