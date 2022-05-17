from .models import Device

def decide_energy_prices(energy_measurements):
    for energy_data in energy_measurements:
        

        device = Device.objects.get(id=energy_data["device_id"])
        energy_data["calculated_price"] = 0.68*energy_data["energy_value"]
        energy_data["energy_source"] = "public grid"
    return energy_measurements

    # if decyzja == 'generuj':
    #     smart_building.push_raports()

# TWORZENIE RAPORTU:
# som_dev = SmartHomeDevice({"id": 1})
#         some_rap = SmartHomeDeviceRaport({"turned_on":"2022-05-09 16:31:00", "turned_off": "2022-05-09 17:30:00"})
#         resp = som_dev.push_raports([some_rap])
#         return Response(resp.json(), status=resp.status_code)
