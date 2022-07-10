# from collections import OrderedDict
# from datetime import datetime, timedelta
# from decimal import ROUND_HALF_UP, Decimal

# import pytest
# from mock import patch
# from rest_framework.test import APIClient
# from services.smart_home import SmartHomeChargeStateRaport
# from smarthome.constants import EnergySource as sources
# from smarthome.energy_calculators import (EnergyStorageCalculator,
#                                           GridSurplusEnergyCalculator,
#                                           PhotovoltaicsEnergyCalculator,
#                                           PublicGridEnergyCalculator)
# from smarthome.energy_calculators.energy_exchange_calc import \
#     EnergyExchangeCalculator
# from smarthome.measurements_manager import EnergyMeasurementsManager
# from smarthome.models import (Building, EnergyDailyMeasurement,
#                               EnergyGenerator, EnergyReceiver, EnergyStorage,
#                               EnergySurplusLossRaport, EnergySurplusRaport,
#                               ExchangeEnergyStorageRaport)
# from users.models import User

# from .data import (
#     exchange_home_setups_list,
#     multiwindowed_all_sources_and_exchange_energy_in_first_window_home_setups_list,
#     multiwindowed_all_sources_and_exchange_energy_in_second_window_home_setups_list,
#     multiwindowed_all_sources_home_setups_list,
#     multiwindowed_photovoltaics_home_setups_list,
#     multiwindowed_photovoltaics_storage_home_setups_list,
#     photovoltaics_only_home_setups_list, storage_home_setups_list)

# import requests_mock


# @pytest.mark.django_db
# class TestEnergy:
#     client = APIClient()

#     def setUpBuildingSinglePhotovoltaics(self, requests_mock):
#         requests_mock=self._mock_requests(requests_mock)
#         user = User.objects.create(email="defaultuser@email.com", password="defaultpassword")
#         building = Building.objects.create(user=user, name="house")
#         receiver = EnergyReceiver.objects.create(building=building, name="bulb", state=False, device_power=60, supply_voltage=8)
#         generator = EnergyGenerator.objects.create(name='photovoltaics1', building=building, generation_power = 635.0)
#         return {
#             "building": building,
#             "devices": [receiver],
#             "generators": [generator],
#         }
    
#     def _mock_requests(self, requests_mock):
#         requests_mock.real_http = True
#         for i in range(1000):
#             requests_mock.get('http://simulation:8000/api/users/')
#             requests_mock.post('http://simulation:8000/api/users/')

#             requests_mock.get(f'http://simulation:8000/api/users/{i}/buildings/')
#             requests_mock.post(f'http://simulation:8000/api/users/{i}/buildings/')

#             requests_mock.get(f'http://simulation:8000/api/buildings/{i}/devices/')
#             requests_mock.post(f'http://simulation:8000/api/buildings/{i}/devices/')

#             requests_mock.get(f'http://simulation:8000/api/devices/{i}/device-raports/')
#             requests_mock.post(f'http://simulation:8000/api/devices/{i}/device-raports/')
#         return requests_mock

#     def _get_energy_price(self, value, price):
#         grosze = Decimal("0.01")
#         full_price = price * float(value)
#         return Decimal(full_price).quantize(grosze, ROUND_HALF_UP)

#     def _get_price_by_source(self, source):
#         return {
#             sources.PHOTOVOLTAICS: 0,
#             sources.GRID_SURPLUS: 0,
#             sources.ENERGY_STORAGE: 0,
#             sources.PUBLIC_GRID: 0.68,
#             sources.ENERGY_EXCHANGE: 0.6,
#         }.get(source)
        
#     @pytest.mark.parametrize('home_setup', photovoltaics_only_home_setups_list)
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_1_hour(self, mock_measurements, home_setup, requests_mock):
#         """Check energy usage calculations in home for single time window (59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 10,59,59)

#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
#         home_setup = home_setup.get("first_window")

#         energy_sources = OrderedDict([
#                 (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                 (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                 (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                 ])


#         receiver_energy = home_setup.get("receiver_energy", 0)
#         generator_energy = home_setup.get("generator_energy", 0)

#         measurements = [
#             EnergyDailyMeasurement(device=receiver, datetime=end_date,energy_value=receiver_energy),
#             EnergyDailyMeasurement(device=generator, datetime=end_date,energy_value=generator_energy)
#         ]
#         mock_measurements.return_value = measurements

#         measurements_manager = EnergyMeasurementsManager(building, energy_sources)
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)

#         first_raport = source_raport[0]
#         home_sources_data = home_setup.get("sources")

#         photovoltaics_data = first_raport.energy_sources[sources.PHOTOVOLTAICS]
#         photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#         photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#         assert photovoltaics_data["value"] == photovoltaics_value
#         assert photovoltaics_data["price"] == self._get_energy_price(photovoltaics_value, photovoltaics_price)

#         grid_surplus_data = first_raport.energy_sources[sources.GRID_SURPLUS]
#         grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#         grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#         assert grid_surplus_data["value"] == grid_surplus_value
#         assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)

#         public_grid_data = first_raport.energy_sources[sources.PUBLIC_GRID]
#         public_grid_value = home_sources_data.get("public_grid_used", 0)
#         public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#         assert public_grid_data["value"] == public_grid_value
#         assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#         first_surplus_raport = surplus_raport[0]
#         home_surpluses_data = home_setup.get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_iteration_value_transfered = grid_surplus.get("surplus_iteration_value_transfered", 0)
#         surplus_total_value = grid_surplus.get("surplus_total_value")
#         surplus_energy_loss = grid_surplus.get("energy_loss")

#         grid_surplus_data = first_surplus_raport[sources.GRID_SURPLUS]
#         assert grid_surplus_data == surplus_iteration_value_transfered

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert surplus.value == surplus_total_value

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert surplus_loss.value == surplus_energy_loss

#     @pytest.mark.parametrize('home_setup', storage_home_setups_list)
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_1_hour_with_storage(self, mock_storage, mock_measurements, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage in single time window (59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 10,59,59)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         home_setup = home_setup.get("first_window")

#         energy_sources = OrderedDict([
#                 (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                 (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                 (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                 (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                 ])


#         receiver_energy = home_setup.get("receiver_energy", 0)
#         generator_energy = home_setup.get("generator_energy", 0)


#         measurements = [
#             EnergyDailyMeasurement(device=receiver, datetime=end_date,energy_value=receiver_energy),
#             EnergyDailyMeasurement(device=generator, datetime=end_date,energy_value=generator_energy)
#         ]
#         storage_measurements = [
#             SmartHomeChargeStateRaport({"device":storage, "date":start_date, "charge_value":initial_storage_charge_value})
#         ]

#         mock_storage.return_value = storage_measurements
#         mock_measurements.return_value = measurements

#         measurements_manager = EnergyMeasurementsManager(building, energy_sources)
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)

#         first_raport = source_raport[0]
#         home_sources_data = home_setup.get("sources")

#         photovoltaics_data = first_raport.energy_sources[sources.PHOTOVOLTAICS]
#         photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#         photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#         assert round(photovoltaics_data["value"],5) == photovoltaics_value
#         assert photovoltaics_data["price"] == self._get_energy_price(photovoltaics_value, photovoltaics_price)

#         grid_surplus_data = first_raport.energy_sources[sources.GRID_SURPLUS]
#         grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#         grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#         assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#         assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)


#         energy_storage_data = first_raport.energy_sources[sources.ENERGY_STORAGE]
#         energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#         energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)
#         assert round(energy_storage_data["value"],5) == energy_storage_value
#         assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#         public_grid_data = first_raport.energy_sources[sources.PUBLIC_GRID]
#         public_grid_value = home_sources_data.get("public_grid_used", 0)
#         public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#         assert round(public_grid_data["value"],5) == public_grid_value
#         assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#         first_surplus_raport = surplus_raport[0]
#         home_surpluses_data = home_setup.get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_iteration_value_transfered = grid_surplus.get("surplus_iteration_value_transfered", 0)
#         surplus_total_value = grid_surplus.get("surplus_total_value")
#         surplus_energy_loss = grid_surplus.get("energy_loss")

#         grid_surplus_data = first_surplus_raport[sources.GRID_SURPLUS]
#         assert round(grid_surplus_data, 5) == surplus_iteration_value_transfered

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == surplus_total_value

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss

#         storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#         iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#         total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#         storage_surplus_data = first_surplus_raport[sources.ENERGY_STORAGE]
#         assert round(storage_surplus_data, 5) == iteration_energy_stored

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == total_energy_in_storage



#     @pytest.mark.parametrize('home_setup', exchange_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @patch('smarthome.energy_manager.BuildingEnergyManager._set_up_exchange')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_1_hour_with_storage_and_exchange(self, mock_exchange, mock_storage, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in single time window (59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 10,59,59)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source
#         mock_exchange.return_value = None

#         exchange_total_value = home_setup.get("exchange_total_value", 0)
#         exchange_remaining_value = home_setup.get("exchange_remained_value",0)
#         ExchangeEnergyStorageRaport.objects.create(building=building,date_time_from=start_date, date_time_to=end_date,total_value=exchange_total_value, remained_value=exchange_remaining_value, purchase_price=self._get_price_by_source(sources.ENERGY_EXCHANGE))
  

#         home_setup = home_setup.get("first_window")

#         energy_sources = OrderedDict([
#                 (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                 (sources.ENERGY_EXCHANGE, EnergyExchangeCalculator),
#                 (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                 (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                 (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                 ])

#         receiver_energy = home_setup.get("receiver_energy", 0)
#         generator_energy = home_setup.get("generator_energy", 0)


#         measurements = [
#             EnergyDailyMeasurement(device=receiver, datetime=end_date,energy_value=receiver_energy),
#             EnergyDailyMeasurement(device=generator, datetime=end_date,energy_value=generator_energy)
#         ]
#         storage_measurements = [
#             SmartHomeChargeStateRaport({"device":storage, "date":start_date, "charge_value":initial_storage_charge_value})
#         ]

#         mock_storage.return_value = storage_measurements
#         mock_measurements.return_value = measurements

#         measurements_manager = EnergyMeasurementsManager(building, energy_sources)
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)

#         first_raport = source_raport[0]
#         home_sources_data = home_setup.get("sources")

#         photovoltaics_data = first_raport.energy_sources[sources.PHOTOVOLTAICS]
#         photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#         photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#         assert round(photovoltaics_data["value"],5) == photovoltaics_value
#         assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#         energy_exchange_data = first_raport.energy_sources[sources.ENERGY_EXCHANGE]
#         exchange_energy_value = home_sources_data.get("exchange_energy_used", 0)
#         exchange_energy_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
#         assert round(energy_exchange_data["value"],5) == exchange_energy_value
#         assert energy_exchange_data["price"] == self._get_energy_price(exchange_energy_value, exchange_energy_price)

#         grid_surplus_data = first_raport.energy_sources[sources.GRID_SURPLUS]
#         grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#         grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#         assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#         assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)


#         energy_storage_data = first_raport.energy_sources[sources.ENERGY_STORAGE]
#         energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#         energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)

#         assert round(energy_storage_data["value"],5) == energy_storage_value
#         assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#         public_grid_data = first_raport.energy_sources[sources.PUBLIC_GRID]
#         public_grid_value = home_sources_data.get("public_grid_used", 0)
#         public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#         assert round(public_grid_data["value"],5) == public_grid_value
#         assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#         first_surplus_raport = surplus_raport[0]
#         home_surpluses_data = home_setup.get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_iteration_value_transfered = grid_surplus.get("surplus_iteration_value_transfered", 0)
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         grid_surplus_data = first_surplus_raport[sources.GRID_SURPLUS]
#         assert round(grid_surplus_data, 5) == surplus_iteration_value_transfered

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()
  

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value, 5) == surplus_total_value

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss

#         storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#         iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#         total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#         storage_surplus_data = first_surplus_raport[sources.ENERGY_STORAGE]
#         assert round(storage_surplus_data, 5) == iteration_energy_stored

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == initial_storage_charge_value + iteration_energy_stored - energy_storage_value
#         assert round(storage_calc_capacity, 5) == total_energy_in_storage

#         energy_exchange_state = ExchangeEnergyStorageRaport.objects.filter(building=building).last()
#         assert round(energy_exchange_state.remained_value,5) == round(exchange_remaining_value - exchange_energy_value,5)


#     @pytest.mark.parametrize('home_setup', multiwindowed_all_sources_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @patch('smarthome.energy_manager.BuildingEnergyManager._set_up_exchange')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_2_hour_with_storage_and_exchange_with_windows(self, mock_exchange, mock_storage, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in double time window (2*59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 11,59,59)

#         measurements_time = datetime(2022,3,29, 10,50,0)
#         exchange_end_time = datetime(2022,3,29, 12,50,0)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source
#         mock_exchange.return_value = None

#         exchange_total_value = home_setup.get("exchange_total_value", 0)
#         exchange_initial_remained_value = home_setup.get("exchange_remained_value",0)
#         ExchangeEnergyStorageRaport.objects.create(building=building,date_time_from=start_date, date_time_to=exchange_end_time,total_value=exchange_total_value, remained_value=exchange_initial_remained_value, purchase_price=self._get_price_by_source(sources.ENERGY_EXCHANGE))
  
#         energy_sources = OrderedDict([
#                     (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                     (sources.ENERGY_EXCHANGE, EnergyExchangeCalculator),
#                     (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                     (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                     (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                     ])
#         storage_measurements = [
#             SmartHomeChargeStateRaport({"device":storage, "date":start_date, "charge_value":initial_storage_charge_value})
#         ]

#         mock_storage.return_value = storage_measurements

#         measurements = []
#         measurements_manager = EnergyMeasurementsManager(building, energy_sources) 

#         storage_energy_stored_sum = 0
#         storage_energy_used_sum = 0
#         exchange_energy_used_sum = 0
#         grid_surplus_energy_used_sum = 0
#         grid_surplus_energy_transfered_sum = 0
#         for window_setup in home_setup.get("windows"):
#             receiver_energy = window_setup.get("receiver_energy", 0)
#             generator_energy = window_setup.get("generator_energy", 0)

#             window_sources = window_setup.get("sources")
#             window_surpluses = window_setup.get("surpluses")

#             storage_energy_stored_sum += window_surpluses[sources.ENERGY_STORAGE].get("iteration_energy_stored", 0)
#             storage_energy_used_sum += window_sources.get("energy_storage_used", 0)
#             exchange_energy_used_sum += window_sources.get("exchange_energy_used", 0)
#             grid_surplus_energy_used_sum += window_sources.get("grid_surplus_used",0)
#             grid_surplus_energy_transfered_sum += window_surpluses[sources.GRID_SURPLUS].get("surplus_iteration_value_transfered", 0)
#             measurements.append([
#                 EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
#                 EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=generator_energy)
#             ])
#             measurements_time += timedelta(minutes=30)


#         mock_measurements.side_effect = measurements
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)
#         for i, window_setup in enumerate(home_setup.get("windows")):
#             current_raport = source_raport[i]
#             home_sources_data = window_setup.get("sources")

#             photovoltaics_data = current_raport.energy_sources[sources.PHOTOVOLTAICS]
#             photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#             photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#             assert round(photovoltaics_data["value"],5) == photovoltaics_value
#             assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#             energy_exchange_data = current_raport.energy_sources[sources.ENERGY_EXCHANGE]
#             exchange_energy_value = home_sources_data.get("exchange_energy_used", 0)
#             exchange_energy_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
#             assert round(energy_exchange_data["value"],5) == exchange_energy_value
#             assert energy_exchange_data["price"] == self._get_energy_price(exchange_energy_value, exchange_energy_price)

#             grid_surplus_data = current_raport.energy_sources[sources.GRID_SURPLUS]
#             grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#             grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#             assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#             assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)


#             energy_storage_data = current_raport.energy_sources[sources.ENERGY_STORAGE]
#             energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#             energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)
#             assert round(energy_storage_data["value"],5) == energy_storage_value
#             assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#             public_grid_data = current_raport.energy_sources[sources.PUBLIC_GRID]
#             public_grid_value = home_sources_data.get("public_grid_used", 0)
#             public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#             assert round(public_grid_data["value"],5) == public_grid_value
#             assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#             next_surplus_raport = surplus_raport[i]
#             home_surpluses_data = window_setup.get("surpluses", {})

#             grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#             surplus_iteration_value = grid_surplus.get("surplus_iteration_value_transfered", 0)

#             grid_surplus_data = next_surplus_raport[sources.GRID_SURPLUS]
#             assert round(grid_surplus_data, 5) == surplus_iteration_value

#             storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#             iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#             total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#             storage_surplus_data = next_surplus_raport[sources.ENERGY_STORAGE]
            
#             assert round(storage_surplus_data, 5) == round(iteration_energy_stored, 5)

#         energy_exchange_state = ExchangeEnergyStorageRaport.objects.filter(building=building).last()
#         assert round(energy_exchange_state.remained_value,5) == round(exchange_initial_remained_value - exchange_energy_used_sum,5)

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == round(total_energy_in_storage,5)
#         assert round(storage_calc_capacity, 5) == round(initial_storage_charge_value + storage_energy_stored_sum - storage_energy_used_sum, 5)

#         home_surpluses_data = home_setup.get("windows")[-1].get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == round(surplus_total_value, 5)

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss

#     @pytest.mark.parametrize('home_setup', multiwindowed_all_sources_and_exchange_energy_in_first_window_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @patch('smarthome.energy_manager.BuildingEnergyManager._set_up_exchange')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_2_hour_with_storage_and_energy_exchange_in_first_window(self, mock_exchange, mock_storage, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in double time window (2*59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 11,59,59)

#         measurements_time = datetime(2022,3,29, 10,50,0)
#         exchange_end_time = datetime(2022,3,29, 11,0,0)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source
#         mock_exchange.return_value = None

#         exchange_total_value = home_setup.get("exchange_total_value", 0)
#         exchange_initial_remained_value = home_setup.get("exchange_remained_value",0)
#         ExchangeEnergyStorageRaport.objects.create(building=building,date_time_from=start_date, date_time_to=exchange_end_time,total_value=exchange_total_value, remained_value=exchange_initial_remained_value, purchase_price=self._get_price_by_source(sources.ENERGY_EXCHANGE))
  
#         energy_sources = OrderedDict([
#                     (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                     (sources.ENERGY_EXCHANGE, EnergyExchangeCalculator),
#                     (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                     (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                     (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                     ])
#         storage_measurements = [
#             SmartHomeChargeStateRaport({"device":storage, "date":start_date, "charge_value":initial_storage_charge_value})
#         ]

#         mock_storage.return_value = storage_measurements

#         measurements = []
#         measurements_manager = EnergyMeasurementsManager(building, energy_sources) 

#         storage_energy_stored_sum = 0
#         storage_energy_used_sum = 0
#         exchange_energy_used_sum = 0
#         grid_surplus_energy_used_sum = 0
#         grid_surplus_energy_transfered_sum = 0
#         for window_setup in home_setup.get("windows"):
#             receiver_energy = window_setup.get("receiver_energy", 0)
#             generator_energy = window_setup.get("generator_energy", 0)

#             window_sources = window_setup.get("sources")
#             window_surpluses = window_setup.get("surpluses")

#             storage_energy_stored_sum += window_surpluses[sources.ENERGY_STORAGE].get("iteration_energy_stored", 0)
#             storage_energy_used_sum += window_sources.get("energy_storage_used", 0)
#             exchange_energy_used_sum += window_sources.get("exchange_energy_used", 0)
#             grid_surplus_energy_used_sum += window_sources.get("grid_surplus_used",0)
#             grid_surplus_energy_transfered_sum += window_surpluses[sources.GRID_SURPLUS].get("surplus_iteration_value_transfered", 0)
#             measurements.append([
#                 EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
#                 EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=generator_energy)
#             ])
#             measurements_time += timedelta(minutes=30)


#         mock_measurements.side_effect = measurements
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)
#         for i, window_setup in enumerate(home_setup.get("windows")):
#             current_raport = source_raport[i]
#             home_sources_data = window_setup.get("sources")

#             photovoltaics_data = current_raport.energy_sources[sources.PHOTOVOLTAICS]
#             photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#             photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#             assert round(photovoltaics_data["value"],5) == photovoltaics_value
#             assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#             energy_exchange_data = current_raport.energy_sources[sources.ENERGY_EXCHANGE]
#             exchange_energy_value = home_sources_data.get("exchange_energy_used", 0)
#             exchange_energy_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
#             assert round(energy_exchange_data["value"],5) == exchange_energy_value
#             assert energy_exchange_data["price"] == self._get_energy_price(exchange_energy_value, exchange_energy_price)

#             grid_surplus_data = current_raport.energy_sources[sources.GRID_SURPLUS]
#             grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#             grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#             assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#             assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)


#             energy_storage_data = current_raport.energy_sources[sources.ENERGY_STORAGE]
#             energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#             energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)
#             assert round(energy_storage_data["value"],5) == energy_storage_value
#             assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#             public_grid_data = current_raport.energy_sources[sources.PUBLIC_GRID]
#             public_grid_value = home_sources_data.get("public_grid_used", 0)
#             public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#             assert round(public_grid_data["value"],5) == public_grid_value
#             assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#             next_surplus_raport = surplus_raport[i]
#             home_surpluses_data = window_setup.get("surpluses", {})

#             grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#             surplus_iteration_value = grid_surplus.get("surplus_iteration_value_transfered", 0)

#             grid_surplus_data = next_surplus_raport[sources.GRID_SURPLUS]
#             assert round(grid_surplus_data, 5) == surplus_iteration_value

#             storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#             iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#             total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#             storage_surplus_data = next_surplus_raport[sources.ENERGY_STORAGE]
            
#             assert round(storage_surplus_data, 5) == round(iteration_energy_stored, 5)

#         energy_exchange_state = ExchangeEnergyStorageRaport.objects.filter(building=building).last()
#         assert round(energy_exchange_state.remained_value,5) == round(exchange_initial_remained_value - exchange_energy_used_sum,5)

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == round(total_energy_in_storage,5)
#         assert round(storage_calc_capacity, 5) == round(initial_storage_charge_value + storage_energy_stored_sum - storage_energy_used_sum, 5)

#         home_surpluses_data = home_setup.get("windows")[-1].get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == round(surplus_total_value, 5)

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss

#     @pytest.mark.parametrize('home_setup', multiwindowed_all_sources_and_exchange_energy_in_second_window_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @patch('smarthome.energy_manager.BuildingEnergyManager._set_up_exchange')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_2_hour_with_storage_and_energy_exchange_in_second_window(self, mock_exchange, mock_storage, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in double time window (2*59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 11,59,59)

#         measurements_time = datetime(2022,3,29, 10,50,0)
#         exchange_start_time = datetime(2022,3,29, 11,0,0)
#         exchange_end_time = datetime(2022,3,29, 12,50,0)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source
#         mock_exchange.return_value = None

#         exchange_total_value = home_setup.get("exchange_total_value", 0)
#         exchange_initial_remained_value = home_setup.get("exchange_remained_value",0)
#         ExchangeEnergyStorageRaport.objects.create(building=building,date_time_from=exchange_start_time, date_time_to=exchange_end_time,total_value=exchange_total_value, remained_value=exchange_initial_remained_value, purchase_price=self._get_price_by_source(sources.ENERGY_EXCHANGE))
  
#         energy_sources = OrderedDict([
#                     (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                     (sources.ENERGY_EXCHANGE, EnergyExchangeCalculator),
#                     (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                     (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                     (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                     ])
        
#         measurements = []
#         storage_measurements = []
#         measurements_manager = EnergyMeasurementsManager(building, energy_sources) 

#         storage_energy_stored_sum = 0
#         storage_energy_used_sum = 0
#         exchange_energy_used_sum = 0
#         grid_surplus_energy_used_sum = 0
#         grid_surplus_energy_transfered_sum = 0
#         storage_charge_value = initial_storage_charge_value
#         for window_setup in home_setup.get("windows"):
#             receiver_energy = window_setup.get("receiver_energy", 0)
#             generator_energy = window_setup.get("generator_energy", 0)

#             window_sources = window_setup.get("sources")
#             window_surpluses = window_setup.get("surpluses")

#             storage_energy_stored_sum += window_surpluses[sources.ENERGY_STORAGE].get("iteration_energy_stored", 0)
#             storage_energy_used_sum += window_sources.get("energy_storage_used", 0)
#             exchange_energy_used_sum += window_sources.get("exchange_energy_used", 0)
#             grid_surplus_energy_used_sum += window_sources.get("grid_surplus_used",0)
#             grid_surplus_energy_transfered_sum += window_surpluses[sources.GRID_SURPLUS].get("surplus_iteration_value_transfered", 0)
#             measurements.append([
#                 EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
#                 EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=generator_energy)
#             ])

#             storage_measurements.append([
#             SmartHomeChargeStateRaport({"device":storage, "date":measurements_time, "charge_value":storage_charge_value}),
#             ])
#             storage_charge_value = storage_charge_value-window_sources.get("energy_storage_used", 0)+window_surpluses[sources.ENERGY_STORAGE].get("iteration_energy_stored", 0)
        
#             measurements_time += timedelta(minutes=30)

#         mock_storage.side_effect = storage_measurements
#         mock_measurements.side_effect = measurements
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)
#         for i, window_setup in enumerate(home_setup.get("windows")):
#             current_raport = source_raport[i]
#             home_sources_data = window_setup.get("sources")

#             photovoltaics_data = current_raport.energy_sources[sources.PHOTOVOLTAICS]
#             photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#             photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#             assert round(photovoltaics_data["value"],5) == photovoltaics_value
#             assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#             energy_exchange_data = current_raport.energy_sources[sources.ENERGY_EXCHANGE]
#             exchange_energy_value = home_sources_data.get("exchange_energy_used", 0)
#             exchange_energy_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_EXCHANGE)
#             assert round(energy_exchange_data["value"],5) == exchange_energy_value
#             assert energy_exchange_data["price"] == self._get_energy_price(exchange_energy_value, exchange_energy_price)

#             grid_surplus_data = current_raport.energy_sources[sources.GRID_SURPLUS]
#             grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#             grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#             assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#             assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)


#             energy_storage_data = current_raport.energy_sources[sources.ENERGY_STORAGE]
#             energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#             energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)
#             assert round(energy_storage_data["value"],5) == energy_storage_value
#             assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#             public_grid_data = current_raport.energy_sources[sources.PUBLIC_GRID]
#             public_grid_value = home_sources_data.get("public_grid_used", 0)
#             public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#             assert round(public_grid_data["value"],5) == public_grid_value
#             assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#             next_surplus_raport = surplus_raport[i]
#             home_surpluses_data = window_setup.get("surpluses", {})

#             grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#             surplus_iteration_value = grid_surplus.get("surplus_iteration_value_transfered", 0)

#             grid_surplus_data = next_surplus_raport[sources.GRID_SURPLUS]
#             assert round(grid_surplus_data, 5) == surplus_iteration_value

#             storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#             iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#             total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#             storage_surplus_data = next_surplus_raport[sources.ENERGY_STORAGE]
            
#             assert round(storage_surplus_data, 5) == round(iteration_energy_stored, 5)

#         energy_exchange_state = ExchangeEnergyStorageRaport.objects.filter(building=building).last()
#         assert round(energy_exchange_state.remained_value,5) == round(exchange_initial_remained_value - exchange_energy_used_sum,5)

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == round(total_energy_in_storage,5)
#         assert round(storage_calc_capacity, 5) == round(initial_storage_charge_value + storage_energy_stored_sum - storage_energy_used_sum, 5)

#         home_surpluses_data = home_setup.get("windows")[-1].get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == round(surplus_total_value, 5)

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss


#     @pytest.mark.parametrize('home_setup', multiwindowed_photovoltaics_storage_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_1_hour_photovoltaics_and_storage_with_windows(self, mock_storage, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in double time window (2*59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]


#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 11,59,59)

#         measurements_time = datetime(2022,3,29, 10,50,0)

#         storage_capacity = home_setup.get("storage_capacity", 6)
#         storage_voltage = home_setup.get("storage_voltage", 24)
#         initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
#         storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source

#         energy_sources = OrderedDict([
#                     (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                     (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                     (sources.ENERGY_STORAGE, EnergyStorageCalculator),
#                     (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                     ])
#         storage_measurements = [
#             SmartHomeChargeStateRaport({"device":storage, "date":start_date, "charge_value":initial_storage_charge_value})
#         ]

#         mock_storage.return_value = storage_measurements

#         measurements = []
#         measurements_manager = EnergyMeasurementsManager(building, energy_sources) 

#         storage_energy_stored_sum = 0
#         storage_energy_used_sum = 0
#         grid_surplus_energy_used_sum = 0
#         grid_surplus_energy_transfered_sum = 0
#         for window_setup in home_setup.get("windows"):
#             receiver_energy = window_setup.get("receiver_energy", 0)
#             generator_energy = window_setup.get("generator_energy", 0)

#             window_sources = window_setup.get("sources")
#             window_surpluses = window_setup.get("surpluses")

#             storage_energy_stored_sum += window_surpluses[sources.ENERGY_STORAGE].get("iteration_energy_stored", 0)
#             storage_energy_used_sum += window_sources.get("energy_storage_used", 0)
#             grid_surplus_energy_used_sum += window_sources.get("grid_surplus_used",0)
#             grid_surplus_energy_transfered_sum += window_surpluses[sources.GRID_SURPLUS].get("surplus_iteration_value_transfered", 0)
#             measurements.append([
#                 EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
#                 EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=generator_energy)
#             ])
#             measurements_time += timedelta(minutes=30)


#         mock_measurements.side_effect = measurements
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)
#         for i, window_setup in enumerate(home_setup.get("windows")):
#             current_raport = source_raport[i]
#             home_sources_data = window_setup.get("sources")

#             photovoltaics_data = current_raport.energy_sources[sources.PHOTOVOLTAICS]
#             photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#             photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#             assert round(photovoltaics_data["value"],5) == photovoltaics_value
#             assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#             grid_surplus_data = current_raport.energy_sources[sources.GRID_SURPLUS]
#             grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#             grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#             assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#             assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)

#             energy_storage_data = current_raport.energy_sources[sources.ENERGY_STORAGE]
#             energy_storage_value = home_sources_data.get("energy_storage_used", 0)
#             energy_storage_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.ENERGY_STORAGE)
#             assert round(energy_storage_data["value"],5) == energy_storage_value
#             assert energy_storage_data["price"] == self._get_energy_price(energy_storage_value, energy_storage_price)

#             public_grid_data = current_raport.energy_sources[sources.PUBLIC_GRID]
#             public_grid_value = home_sources_data.get("public_grid_used", 0)
#             public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#             assert round(public_grid_data["value"],5) == public_grid_value
#             assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#             next_surplus_raport = surplus_raport[i]
#             home_surpluses_data = window_setup.get("surpluses", {})

#             grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#             surplus_iteration_value = grid_surplus.get("surplus_iteration_value_transfered", 0)

#             grid_surplus_data = next_surplus_raport[sources.GRID_SURPLUS]
#             assert round(grid_surplus_data, 5) == surplus_iteration_value

#             storage_surplus = home_surpluses_data.get(sources.ENERGY_STORAGE, {})
#             iteration_energy_stored = storage_surplus.get("iteration_energy_stored", 0)
#             total_energy_in_storage = storage_surplus.get("total_energy_in_storage")
#             storage_surplus_data = next_surplus_raport[sources.ENERGY_STORAGE]
            
#             assert round(storage_surplus_data, 5) == round(iteration_energy_stored, 5)

#         storage_calc = measurements_manager._energy_manager._sources_calculators[sources.ENERGY_STORAGE]._storage_devices_data[storage]
#         storage_calc_capacity = storage_calc.get("current_capacity")
#         assert round(storage_calc_capacity, 5) == round(total_energy_in_storage,5)
#         assert round(storage_calc_capacity, 5) == round(initial_storage_charge_value + storage_energy_stored_sum - storage_energy_used_sum, 5)

#         home_surpluses_data = home_setup.get("windows")[-1].get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == round(surplus_total_value, 5)

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss

#     @pytest.mark.parametrize('home_setup', multiwindowed_photovoltaics_home_setups_list)
#     @patch('smarthome.price_manager.PriceManager.get_price_by_source')
#     @patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
#     @requests_mock.Mocker(kw="requests_mock")
#     def test_calculate_energy_usage_for_1_hour_photovoltaics_with_windows(self, mock_measurements,mock_pricer, home_setup, requests_mock):
#         """Check energy usage calculations in home with storage and energy exchange in double time window (2*59 minutes)"""
#         requests_mock=self._mock_requests(requests_mock)
#         db = self.setUpBuildingSinglePhotovoltaics(requests_mock)
#         building = db["building"]
#         receiver = db["devices"][0]
#         generator = db["generators"][0]

#         start_date = datetime(2022,3,29, 10,0,0)
#         end_date = datetime(2022,3,29, 11,59,59)

#         measurements_time = datetime(2022,3,29, 10,50,0)
   
#         initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
#         EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date, usage_type = EnergySurplusRaport.TRANSFER)
        
#         mock_pricer.side_effect = self._get_price_by_source

#         energy_sources = OrderedDict([
#                     (sources.PHOTOVOLTAICS, PhotovoltaicsEnergyCalculator),
#                     (sources.GRID_SURPLUS, GridSurplusEnergyCalculator),
#                     (sources.PUBLIC_GRID, PublicGridEnergyCalculator),
#                     ])

#         measurements = []
#         measurements_manager = EnergyMeasurementsManager(building, energy_sources) 

#         grid_surplus_energy_used_sum = 0
#         grid_surplus_energy_transfered_sum = 0
#         for window_setup in home_setup.get("windows"):
#             receiver_energy = window_setup.get("receiver_energy", 0)
#             generator_energy = window_setup.get("generator_energy", 0)

#             window_sources = window_setup.get("sources")
#             window_surpluses = window_setup.get("surpluses")

#             grid_surplus_energy_used_sum += window_sources.get("grid_surplus_used",0)
#             grid_surplus_energy_transfered_sum += window_surpluses[sources.GRID_SURPLUS].get("surplus_iteration_value_transfered", 0)
#             measurements.append([
#                 EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
#                 EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=generator_energy)
#             ])
#             measurements_time += timedelta(minutes=30)


#         mock_measurements.side_effect = measurements
#         _, source_raport, surplus_raport = measurements_manager.download_home_energy(start_date, end_date)
#         for i, window_setup in enumerate(home_setup.get("windows")):
#             current_raport = source_raport[i]
#             home_sources_data = window_setup.get("sources")

#             photovoltaics_data = current_raport.energy_sources[sources.PHOTOVOLTAICS]
#             photovoltaics_value = home_sources_data.get("photovoltaics_used", 0)
#             photovoltaics_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PHOTOVOLTAICS)
#             assert round(photovoltaics_data["value"],5) == photovoltaics_value
#             assert photovoltaics_data["price"] == photovoltaics_value * photovoltaics_price

#             grid_surplus_data = current_raport.energy_sources[sources.GRID_SURPLUS]
#             grid_surplus_value = home_sources_data.get("grid_surplus_used", 0)
#             grid_surplus_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.GRID_SURPLUS)
#             assert round(grid_surplus_data["value"], 5) == grid_surplus_value
#             assert grid_surplus_data["price"] == self._get_energy_price(grid_surplus_value, grid_surplus_price)

#             public_grid_data = current_raport.energy_sources[sources.PUBLIC_GRID]
#             public_grid_value = home_sources_data.get("public_grid_used", 0)
#             public_grid_price = measurements_manager._energy_manager._price_manager.get_price_by_source(sources.PUBLIC_GRID)
#             assert round(public_grid_data["value"],5) == public_grid_value
#             assert public_grid_data["price"] == self._get_energy_price(public_grid_value, public_grid_price)

#             next_surplus_raport = surplus_raport[i]
#             home_surpluses_data = window_setup.get("surpluses", {})

#             grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#             surplus_iteration_value = grid_surplus.get("surplus_iteration_value_transfered", 0)

#             grid_surplus_data = next_surplus_raport[sources.GRID_SURPLUS]
#             assert round(grid_surplus_data, 5) == surplus_iteration_value

#         home_surpluses_data = home_setup.get("windows")[-1].get("surpluses", {})
#         grid_surplus = home_surpluses_data.get(sources.GRID_SURPLUS, {})
#         surplus_usage_type = grid_surplus.get("usage_type")
#         surplus_total_value = grid_surplus.get("surplus_total_value", 0)
#         surplus_energy_loss = grid_surplus.get("energy_loss", 0)

#         surplus =  EnergySurplusRaport.objects.filter(building=building).last()

#         assert surplus.usage_type == surplus_usage_type
#         assert round(surplus.value,5) == round(surplus_total_value, 5)

#         if surplus_usage_type == EnergySurplusRaport.TRANSFER:
#             surplus_loss = EnergySurplusLossRaport.objects.filter(building=building).last()
#             assert round(surplus_loss.value,5) == surplus_energy_loss
