from datetime import timedelta
 
 
import pandas as pd
import numpy as np
import datetime
 
 
def generate_weather(fromTime, toTime):
    table = pd.DataFrame()
    format_data = "%Y-%m-% %H:%M:%S.%f"
    # values which changes
    max_energy = 200
    start_time = datetime.datetime(2021, 12, 31, 7, 46, 0)
    end_time = datetime.datetime(2021, 12, 31, 15, 34, 0)
    counting_to_peak = 0
    day = 0
    value_to_fluc = 0
    forecast_value = 0
    to_json = {}
    is_forecast = 0
    rising_value = 0
    actual_energy = 0
    energy_to_save = 0
 
    random_max_energy = 0
    # values to create cloudy weather
    lower_cloudy_time = 0
    higher_cloudy_time = 0
 
    series = pd.date_range(start='2022-01-01', end='2023-01-1', freq="5t")
    for time in series:
 
        # checking if it another day
        if day != time.day:
            day = time.day
            if time < datetime.datetime(start_time.year, 7, 2):
                max_energy += 4
                start_time = start_time - timedelta(minutes=1, seconds=15)
                start_time = start_time + timedelta(days=1)
                end_time = end_time + timedelta(days=1, minutes=1, seconds=50)
            else:
                max_energy = max_energy - 4
                end_time = end_time + timedelta(days=1)
                start_time = start_time + timedelta(days=1, minutes=1, seconds=15)
                end_time = end_time - timedelta(minutes=1, seconds=50)
            if fromTime is not None:
                if fromTime.day <= time.day <= toTime.day and fromTime.month == time.month:
                    counting_to_peak, higher_cloudy_time, is_forecast, lower_cloudy_time, rising_value, value_to_fluc = generate_const_for_day(
                        counting_to_peak, end_time, higher_cloudy_time, is_forecast, lower_cloudy_time, max_energy,
                        rising_value, start_time, value_to_fluc)
                else:
                    continue
            else:
                counting_to_peak, higher_cloudy_time, is_forecast, lower_cloudy_time, rising_value, value_to_fluc = generate_const_for_day(
                    counting_to_peak, end_time, higher_cloudy_time, is_forecast, lower_cloudy_time, max_energy,
                    rising_value, start_time, value_to_fluc)
 
        if end_time > time > start_time:
 
            # check if the sun sunrise or go away
            if rising_value <= 0:
                rising_value = 1
            random_rising_value = np.random.random() * (rising_value * 2)
 
            # rising or falling the value of energy
            if counting_to_peak > 0:
                rising_value = rising_value - value_to_fluc
 
                actual_energy += random_rising_value
                counting_to_peak = counting_to_peak - 1
                if actual_energy < 0:
                    actual_energy = np.random.randint(3, 10)
 
            elif counting_to_peak == 0:
                rising_value = rising_value + value_to_fluc
 
                actual_energy = actual_energy - random_rising_value
                if actual_energy <= 0:
                    actual_energy = np.random.randint(1, 5)
            # add some possibilities that weather might be cloudy
            if lower_cloudy_time < counting_to_peak < higher_cloudy_time:
                energy_to_save = round(actual_energy * (np.random.uniform(low=0.3, high=0.7)), 2)
            else:
                energy_to_save = round(actual_energy, 2)
        else:
            actual_energy = 0
            energy_to_save = round(actual_energy, 2)
        # if the forecast isnot correct
        if is_forecast == 5:
            # the weather is worst
            forecast_value = energy_to_save * np.random.uniform(low=0.6, high=0.7)
        elif is_forecast == 2:
            forecast_value = energy_to_save * np.random.uniform(low=1.3, high=1.4)
        else:
            forecast_value = energy_to_save * np.random.uniform(low=0.97, high=1.03)
        forecast_value = round(forecast_value, 2)
        if fromTime > time or time > toTime:
            continue
        frame = pd.DataFrame(
            {"datetime_to": [time],
             "real": [energy_to_save], "forecast": [forecast_value], })
        table = table.append(frame, ignore_index=True)
        item = {
            str(time): {"real": {"solar_radiation": energy_to_save}, "forecast": {"solar_radiation": forecast_value}}}
        to_json.update(item)
 
    return table
 
 
def generate_const_for_day(counting_to_peak, end_time, higher_cloudy_time, is_forecast, lower_cloudy_time, max_energy,
                           rising_value, start_time, value_to_fluc):
    random_max_energy = np.random.randint(max_energy - 25, max_energy + 50)
    counting_to_peak = round(_getMeanTime(start_time, end_time) / 2)
    rising_value = (random_max_energy / counting_to_peak) + 5
    value_to_fluc = rising_value / counting_to_peak
    lower_cloudy_time = np.random.randint(-counting_to_peak, round(counting_to_peak / 3))
    higher_cloudy_time = np.random.randint(round(-counting_to_peak / 3), counting_to_peak)
    is_forecast = np.random.randint(1, 10)
    return counting_to_peak, higher_cloudy_time, is_forecast, lower_cloudy_time, rising_value, value_to_fluc
 
 
def _getMeanTime(start_time, end_time):
    test = pd.date_range(start_time, end_time, freq="5t")
    return len(test)
