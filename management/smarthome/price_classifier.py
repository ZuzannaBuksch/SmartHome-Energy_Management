from .models import Device

def decide_energy_prices(energy_measurements):
    for energy_data in energy_measurements:
        

        device = Device.objects.get(id=energy_data["device_id"])
        energy_data["calculated_price"] = 0.68*energy_data["energy_value"]
        energy_data["energy_source"] = "public grid"
    return energy_measurements

    # if decyzja == 'generuj':
    #     smart_building.push_raports()
