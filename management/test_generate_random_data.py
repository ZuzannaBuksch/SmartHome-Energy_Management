import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "management.settings")


import django

django.setup()

import json
from datetime import datetime, time, timedelta
from random import randrange

import numpy as np
import pytest
import requests_mock
from mock import patch

from data_generators import energy_market, generate_weather
from services.smart_home import SmartHomeChargeStateRaport
from smarthome.constants import EnergySource as sources
from smarthome.measurements_manager import EnergyMeasurementsManager
from smarthome.models import (Building, EnergyDailyMeasurement,
                              EnergyGenerator, EnergyReceiver, EnergyStorage,
                              EnergySurplusRaport)
from users.models import User


def get_home_setup():
    return []

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def get_home_setup(start_date):
    hours_of_windows = [start_date, start_date+timedelta(hours=1), start_date+timedelta(hours=2)]
    windows_energy_used = []
    for date_ in hours_of_windows:
        if time(16,0,0)<date_.time()<time(23,59,59):
            windows_energy_used.append(np.random.uniform(0.5, 5))
        if time(0,0,0)<date_.time()<time(6,0,0):
            windows_energy_used.append(np.random.uniform(0.03, 0.1))
        else:
            windows_energy_used.append(np.random.uniform(0.5, 2))

    generation_power = 1500 #np.random.randint(400,1800)

    total_storage_capacity = 4 #np.random.randint(3,10)
    total_storage_voltage = 27 #np.random.randint(12, 28) #
    initial_storage_charge_value = np.random.uniform(0,0.4)
    initial_grid_surplus_value = np.random.uniform(0,1)

    return {
        "storage_capacity": total_storage_capacity,
        "storage_voltage": total_storage_voltage,
        "initial_grid_surplus_value": initial_grid_surplus_value,
        "generation_power": generation_power,
        "initial_storage_charge_value": initial_storage_charge_value,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": windows_energy_used[0],
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": windows_energy_used[1],
            },
            { #THIRD TIME WINDOW, 
                "receiver_energy": windows_energy_used[2],
            }

        ]
    }

def time_in_range(start, end, date_time):
    """Returns whether date_time is in the range [start, end]"""
    return start <= date_time <= end


def round_time(dt=None, dateDelta=timedelta(hours=1)):
    """Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
            Stijn Nevens 2014 - Changed to use only datetime objects as variables
    """
    roundTo = dateDelta.total_seconds()

    if dt == None : dt = datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)


def calculate_time_window_photovoltaics_generation(weather_data, generation_power):
    sum_of_energy_in_kwh = 0.0
    for solar_radiation in weather_data['real']:
        diff_in_hours = 0.083
        solar_radiation_coefficient = solar_radiation / 1000
        output_power = generation_power * solar_radiation_coefficient * (1 - 0.05)
        output_power_in_kwh = output_power / 1000 * diff_in_hours
        sum_of_energy_in_kwh += output_power_in_kwh
    return sum_of_energy_in_kwh


def mock_requests(requests_mock, total_count):
    requests_mock.real_http = True
    for i in range(total_count+1):
        requests_mock.get('http://simulation:8000/api/users/')
        requests_mock.post('http://simulation:8000/api/users/')

        requests_mock.get(f'http://simulation:8000/api/users/{i}/buildings/')
        requests_mock.post(f'http://simulation:8000/api/users/{i}/buildings/')

        requests_mock.get(f'http://simulation:8000/api/buildings/{i}/devices/')
        requests_mock.post(f'http://simulation:8000/api/buildings/{i}/devices/')

        requests_mock.get(f'http://simulation:8000/api/devices/{i}/device-raports/')
        requests_mock.post(f'http://simulation:8000/api/devices/{i}/device-raports/')
    return requests_mock

@pytest.mark.django_db
@patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_energy_measurements')
@patch('smarthome.measurements_manager.EnergyMeasurementsManager._get_storage_measurements')
@requests_mock.Mocker(kw="requests_mock")
def test_generate_2_windowed_data(mock_storage, mock_measurements, requests_mock):
    total_count=200
    for i in range(total_count):
        print(i)
        requests_mock=mock_requests(requests_mock, total_count)
        user = User.objects.create(email=f"defaultuser{i}@email.com", password="defaultpassword")
        building = Building.objects.create(user=user, name="house")
        receiver = EnergyReceiver.objects.create(building=building, name="bulb", state=False, device_power=60, supply_voltage=8) #values are not important
        generator = EnergyGenerator.objects.create(name='photovoltaics1', building=building, generation_power = 665)#values are not important

        
        date_str = "%Y-%m-%d %H:%M:%S"
        
        first_date = datetime(2022,5,1,0,0,0)
        last_date = datetime(2022,5,31,20,59,59)

        start_date = round_time(random_date(first_date, last_date))
        end_date = start_date+timedelta(hours=3)

        # start_date = datetime(2022,10,19, 00,00,00)
        # end_date = datetime(2022,10,19, 2,00,00)

        home_setup = get_home_setup(start_date)

        weather_data = generate_weather(start_date, end_date)
        # weather_data = WeatherDataProvider().get_data(start_date, end_date)

        generation_power = home_setup["generation_power"]
        first_window_weather = weather_data[weather_data.datetime_to.between(start_date, start_date+timedelta(minutes=59))]
        sec_window_weather = weather_data[weather_data.datetime_to.between(start_date+timedelta(hours=1), start_date+timedelta(hours=1, minutes=59))]
        third_window_weather = weather_data[weather_data.datetime_to.between(start_date+timedelta(hours=2), end_date)]

        window_generations = [calculate_time_window_photovoltaics_generation(first_window_weather, generation_power)]
        window_generations.append(calculate_time_window_photovoltaics_generation(sec_window_weather, generation_power))
        window_generations.append(calculate_time_window_photovoltaics_generation(third_window_weather, generation_power))

        exchange_data = energy_market(start_date, end_date)
        measurements_time = start_date

        storage_capacity = home_setup.get("storage_capacity")
        storage_voltage = home_setup.get("storage_voltage")
        initial_storage_charge_value = home_setup.get("initial_storage_charge_value", 0)
        storage = EnergyStorage.objects.create(name='storage', building=building, capacity=storage_capacity, battery_voltage=storage_voltage)
        storage_measurements =[
            SmartHomeChargeStateRaport({"device":storage, "date":measurements_time-timedelta(minutes=1), "charge_value":initial_storage_charge_value}),
            ]

        initial_grid_surplus_value = home_setup.get("initial_grid_surplus_value", 0)
        EnergySurplusRaport.objects.create(building = building, value=initial_grid_surplus_value, date_time = start_date-timedelta(minutes=1), usage_type = EnergySurplusRaport.TRANSFER)
        
        
        measurements = []
        measurements_manager = EnergyMeasurementsManager(building) 
        energy_generation = {}
        energy_usage = {}

        for window_setup, window_generation in zip(home_setup.get("windows"), window_generations):
            measurements_time += timedelta(minutes=59)
            receiver_energy = window_setup.get("receiver_energy", 0)
            energy_generation[measurements_time.strftime(date_str)] = window_generation
            energy_usage[measurements_time.strftime(date_str)] = receiver_energy


            measurements.append([
                EnergyDailyMeasurement(device=receiver, datetime=measurements_time,energy_value=receiver_energy),
                EnergyDailyMeasurement(device=generator, datetime=measurements_time,energy_value=window_generation)
            ])


        mock_storage.side_effect = [storage_measurements]
        mock_measurements.side_effect = measurements
        _, sources_raports, surplus_raports = measurements_manager.download_home_energy(start_date, end_date)

        storage_used = {raport.date_time_to.strftime(date_str) : raport.energy_sources.get(sources.ENERGY_STORAGE, {}).get("value",0) for raport in sources_raports}
        storage_stored = {raport.date_time_to.strftime(date_str) : surplus_raport.get(sources.ENERGY_STORAGE, 0) for raport, surplus_raport in zip(sources_raports, surplus_raports)}

        storage_calc_capacities = {}
        window_initial_value = initial_storage_charge_value
        for (date, used), (_, stored) in zip(storage_used.items(), storage_stored.items()):
            window_initial_value-=used
            window_initial_value+=stored
            storage_calc_capacities[date]=window_initial_value

        surplus_used = {raport.date_time_to.strftime(date_str) : raport.energy_sources.get(sources.GRID_SURPLUS, {}).get("value",0) for raport in sources_raports}
        surplus_stored = {raport.date_time_to.strftime(date_str) : surplus.get(sources.GRID_SURPLUS, 0) for raport, surplus in zip(sources_raports, surplus_raports)}
        surplus_data = {}
        window_initial_value = initial_grid_surplus_value*0.8
        for (date, used), (_, stored) in zip(surplus_used.items(), surplus_stored.items()):
            window_initial_value = window_initial_value - used if window_initial_value - used > 0.00001 else 0.0
            window_initial_value += stored
            surplus_data[date]=window_initial_value

        public_grid_data = {raport.date_time_to.strftime(date_str) : raport.energy_sources.get(sources.PUBLIC_GRID, {}).get("value",0) for raport in sources_raports}

        weather_data = weather_data.to_dict()
        fixed_weather_data = {str(date): {"real": real, "forecast": forecast} for date, real, forecast in zip(weather_data["datetime_to"].values(), weather_data["real"].values(), weather_data["forecast"].values())}
        exchange_data = exchange_data.to_dict()
        fixed_exchange_data = {date: value for date, value in zip(exchange_data["datetime"].values(), exchange_data["price"].values())}
        window_data = {
            "start_date": start_date.strftime(date_str),
            "end_date": end_date.strftime(date_str),
            "generation_power": generation_power,
            "initial_storage_charge_value": initial_storage_charge_value,
            "initial_grid_surplus_value": initial_grid_surplus_value,
            "total_storage_capacity": home_setup["storage_capacity"],
            "total_storage_voltage": home_setup["storage_voltage"],
            "energy_generation": energy_generation,
            "energy_usage": energy_usage,
            "energy_storage": storage_calc_capacities,
            "public_grid_data": public_grid_data,
            "surplus_data": surplus_data,
            "weather_data": fixed_weather_data,
            "public_grid_price": 0.69,
            "exchange_data": fixed_exchange_data,
        }
        try:
            with open("random_data_new.json", "r+") as f:
                try:
                    recent_data = json.load(f)
                except json.decoder.JSONDecodeError:
                    recent_data = []
        except FileNotFoundError:
            recent_data = []
        recent_data.append(window_data)
        with open("random_data_new.json", "w+") as f:
            json.dump(recent_data, f, indent=4)

