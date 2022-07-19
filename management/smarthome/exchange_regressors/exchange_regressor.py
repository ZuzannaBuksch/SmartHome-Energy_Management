import math
import pickle
from datetime import timedelta

import numpy as np
import pandas as pd
from data_providers.exchange_prices_data_provider import \
    ExchangePricesDataProvider
from data_providers.weather_data_provider import WeatherDataProvider
from sklearn.preprocessing import StandardScaler

from ..constants import EnergySource as sources
from ..price_manager import PriceManager


class ExchangeEnergyRegressor:
    _regressor = None
    _model_filename = "knn_model.sav"
    _energy_timestamp_data = None
    
    def __init__(self):
        self._load_regression_model()
        pass

    def decide_energy_to_buy(self):
        df = self._collect_energy_data()
        return self._regressor.predict(df)

    def _load_regression_model(self):
        self._regressor = pickle.load(open(self._model_filename, 'rb'))

    def _collect_energy_data(self):
        start_date = self._energy_timestamp_data.pop("start_date")
        end_date = self._energy_timestamp_data["end_date"]
        energy_storage_after_first_window = self._energy_timestamp_data["energy_storage"]
        total_storage_capacity = self._energy_timestamp_data["total_storage_capacity"]
        energy_generation_first_window = self._energy_timestamp_data["energy_generation"] 
        energy_usage_first_window = self._energy_timestamp_data["energy_usage"]
        initial_surplus_value = self._energy_timestamp_data["initial_grid_surplus_value"]
        initial_storage_value = self._energy_timestamp_data["initial_storage_charge_value"]
        used_public_grid_in_first_window = self._energy_timestamp_data["public_grid_data"]
        surplus_after_first_window = self._energy_timestamp_data["surplus_data"]
        generation_power = self._energy_timestamp_data["generation_power"]


        weather_data_third_window = WeatherDataProvider().get_data(start_date+timedelta(hours=2), end_date+timedelta(hours=2)).to_dict()
        forecast_only = {str(date): forecast for date, forecast in zip(weather_data_third_window["datetime_to"].values(), weather_data_third_window["forecast"].values())}

        forecast_values = list(forecast_only.values())
        price_manager = PriceManager()
        price_manager.update_date(start_date, end_date)

        battery_charge = energy_storage_after_first_window / (total_storage_capacity + 0.00001)
        generation_to_usage_ratio = abs(energy_generation_first_window / (energy_usage_first_window + 0.00001))
        print('energy_generation_first_window ', energy_generation_first_window)
        print('energy_usage_first_window ', energy_usage_first_window)
        initial_suprlus_and_storage_to_usage_ratio = (initial_surplus_value + initial_storage_value) / (energy_usage_first_window + 0.00001)

        if_taken_from_public_grid = 1 if used_public_grid_in_first_window != 0 else 0
        if_taken_from_storage =  0 if initial_storage_value > energy_storage_after_first_window else 1
        if_taken_from_surplus = 1 if initial_surplus_value > surplus_after_first_window else 0

        third_window_generation = self._calculate_photovoltaics_generation(forecast_values, generation_power)

        energy_data = {
            'battery_charge' :  battery_charge,
            'generation_to_usage_ratio' : generation_to_usage_ratio,
            'initial_suprlus_and_storage_to_usage_ratio' : abs(initial_suprlus_and_storage_to_usage_ratio),
            'if_taken_from_public_grid' : if_taken_from_public_grid,
            'exchange_price' : price_manager.get_price_by_source(sources.ENERGY_EXCHANGE),
            'grid_price' : price_manager.get_price_by_source(sources.PUBLIC_GRID),
            'if_taken_from_storage' : if_taken_from_storage,
            'if_taken_from_surplus' : if_taken_from_surplus,
            'third_window_generation' : third_window_generation,
        }
        df = pd.DataFrame.from_dict([energy_data], orient='columns')
        df = df.iloc[:, :].values
        return df

    def update_initial_energy_data(self, data):
        self._energy_timestamp_data = data

    def update_energy_data(self, data):
        self._energy_timestamp_data.update(data)

    def _calculate_photovoltaics_generation(self, forecast_values, generation_power):
        sum_of_energy_in_kwh = 0.0
        for value in forecast_values:
            print(value)
            solar_radiation = value
            diff_in_hours = 0.0833
            solar_radiation_coefficient = solar_radiation / 1000
            output_power = generation_power * solar_radiation_coefficient * (1 - 0.05)
            output_power_in_kwh = output_power / 1000 * diff_in_hours
            sum_of_energy_in_kwh += output_power_in_kwh
        return sum_of_energy_in_kwh
