from datetime import datetime
from typing import List

from data_providers import EnergyMarketPriceProvider

from .models import Device, EnergyDailyMeasurement


class PriceClassifier:
    """
    Jeśli zdecydowaliśmy, że kupujemy energię, to ta klasa służy do tego, żeby ustalić,
    czy kupujemy ją z sieci, czy z giełdy.
    Musi więc pobrać cenę energii z giełdy - czy to z pliku, czy z zewnętrznego API.
    """

    def __init__(self):
        self._public_grid_price = 0.68  # PLN
        self._energy_market_price_provider = EnergyMarketPriceProvider()

    def decide_energy_prices(self, energy_measurements: List[EnergyDailyMeasurement]):
        for energy_data in energy_measurements:

            # device = energy_data.device
            energy_market_price = self._energy_market_price_provider.get_price(
                energy_data.datetime
            )

            price = self._public_grid_price
            source = "public grid"
            if energy_market_price < price:
                price = energy_market_price
                source = "energy_market"

            energy_data.calculated_price = price * energy_data.energy_value
            energy_data.energy_source = source
        return energy_measurements

    # if decyzja == 'generuj':
    #     smart_building.push_raports()


# TWORZENIE RAPORTU:
# som_dev = SmartHomeDevice({"id": 1})
#         some_rap = SmartHomeDeviceRaport({"turned_on":"2022-05-09 16:31:00", "turned_off": "2022-05-09 17:30:00"})
#         resp = som_dev.push_raports([some_rap])
#         return Response(resp.json(), status=resp.status_code)
