import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "management.settings")


import django
django.setup()

from data_providers.file_readers import BuildingFileReader
from smarthome.models import Building, Floor, Room
from smarthome.serializers import DeviceSerializer
from users.models import User



class DBPopulater:
    _buildings_filenames = ["data_json/first_scenario_devices.json"]

    def populate_from_file(self):
        for file in self._buildings_filenames:
            user_data = BuildingFileReader(file).read_file()
            user_name = user_data.get("name")
            user_email = user_data.get("email")
            user_password = user_data.get("password")
            
            user, _ = User.objects.get_or_create(name=user_name, email=user_email, password=user_password)
            user_buildings = user_data.get("buildings")
            for building_data in user_buildings:
                building_name = building_data.get("name")
                
                building, _ = Building.objects.get_or_create(name=building_name, user=user)
                building_devices = building_data.get("devices")
                for device_data in building_devices:
                    try:
                        floor, _ = Floor.objects.get_or_create(building=building, level=device_data.pop("floor"))
                    except KeyError:
                        floor = None

                    try:
                        room, _ = Room.objects.get_or_create(name=device_data["room"], floor=floor, area=10)
                        device_data["room"] = room.id
                    except KeyError:
                        pass
                    
                    device_data["resourcetype"] = device_data.get("type")
                    device_data["building"] = building.id
                    serializer = DeviceSerializer(data=device_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

def main():
    db_populater = DBPopulater()
    db_populater.populate_from_file()

if __name__ == "__main__":
    main()
