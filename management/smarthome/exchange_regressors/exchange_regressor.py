from datetime import timedelta
import pickle
import pandas as pd
import numpy as np
import math


from data_providers.exchange_prices_data_provider import ExchangePricesDataProvider
from data_providers.weather_data_provider import WeatherDataProvider
from ..price_manager import PriceManager
from ..constants import EnergySource as sources

class ExchangeEnergyRegressor:
    _regressor = None
    _model_filename = "rf_regression.sav"
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

        weather_data = WeatherDataProvider().get_data(start_date, end_date).to_dict()
        weather_data = {date: {"real": real, "forecast": forecast} for date, real, forecast in zip(weather_data["datetime_to"].values(), weather_data["real"].values(), weather_data["forecast"].values())}
        weather_accuracy = self._calculate_weather_accuracy(weather_data)
        real_only = {k:v.get("real") for k,v in weather_data.items()}
        geometic_mean_solar_radiation_real = ExchangeEnergyRegressor.g_mean(list(real_only.values()))

        forecast_weather_data = WeatherDataProvider().get_data(start_date+timedelta(hours=1), end_date+timedelta(hours=1)).to_dict()
        forecast_only = {str(date): forecast for date, forecast in zip(forecast_weather_data["datetime_to"].values(), forecast_weather_data["forecast"].values())}
        geometic_mean_solar_radiation_forecast = ExchangeEnergyRegressor.g_mean(list(forecast_only.values()))
        
        exchange_data = ExchangePricesDataProvider().get_data(start_date, end_date).to_dict()
        exchange_data = {str(date): value for date, value in zip(exchange_data["datetime"].values(), exchange_data["price"].values())}
        stock_market_trend = self._calculate_stock_market_trend(list(exchange_data.values()))
        
        price_manager = PriceManager()
        price_manager.update_date(start_date, end_date)

        energy_data = {
            **self._energy_timestamp_data,
            "geometic_mean_solar_radiation_real": geometic_mean_solar_radiation_real,
            "geometic_mean_solar_radiation_forecast": geometic_mean_solar_radiation_forecast,
            "weatehr_accuracy": weather_accuracy,
            "stock_market_trend": stock_market_trend,
            "exchange_price": price_manager.get_price_by_source(sources.ENERGY_EXCHANGE),
            "public_grid_price": price_manager.get_price_by_source(sources.PUBLIC_GRID),
        }
        energy_data["energy_usage"] = abs(energy_data["energy_usage"])

        df = pd.DataFrame.from_dict([energy_data])
        df['end_date'] = pd.to_datetime(df['end_date'],infer_datetime_format=True)
        df['end_date']=df['end_date'].apply(lambda x: x.toordinal())
        return df

    def update_initial_energy_data(self, data):
        self._energy_timestamp_data = data

    def update_energy_data(self, data):
        self._energy_timestamp_data.update(data)

    @staticmethod
    def g_mean(x):
        a = np.log(x)
        return np.exp(a.mean())

    def _calculate_stock_market_trend(self, exchange_values):
        mean_ = 0
        F = [0] * (len(exchange_values))
        S = [0] * (len(exchange_values))
        J2 = 0
        J1 = 0
        a = 0.9
        b = 0.9
        krok = 0.0001
        k = 12  # ile krokow do przodu prognoza
        while a < 1:
            while b < 1:
                for t in range(1, len(exchange_values)):
                    F[t] = a * exchange_values[t] + (1 - a) * (F[t - 1] + S[t - 1])
                    S[t] = b * (F[t] - F[t - 1]) + (1 - b) * S[t - 1]
                    if t >= (k + 1):
                        J1 = J1 + math.fabs(F[t - k] + k * S[t - k] - exchange_values[t])
                        J2 = J2 + math.pow(F[t - k] + k * S[t - k] - exchange_values[t], 2)
                b += krok
            a += krok

        mean_ = S[-1]
        return mean_

    def _calculate_weather_accuracy(self, weather_data):
        real_first_window = {k:v.get("real") for k,v in weather_data.items()}
        weather_vals_range = max(real_first_window.values()) - min(real_first_window.values())
        error = 20*weather_vals_range/100
        correct_forecasts_sum = 0
        for  vals in weather_data.values():
            if vals["real"] == vals["forecast"] or (abs(vals["real"] - vals["forecast"])<error):
                correct_forecasts_sum += 1
        return correct_forecasts_sum/len(weather_data.keys())
