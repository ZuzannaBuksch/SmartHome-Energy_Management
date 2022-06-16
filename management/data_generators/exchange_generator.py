import datetime
 
import pandas as pd
import numpy as np

def energy_market(fromTime,toTime):
    min_fluc_value = 0
    max_fluc_value = 8
    table = pd.DataFrame()
    series = pd.date_range(start='2022-01-01', end='2023-01-01', freq="5T")
 
    multiplier = 1
    for time in series:
        if fromTime is not None:
            if fromTime > time or time > toTime:
                continue
            randomNumber = np.random.randint(550, 650)
            if time.minute == 0:
                if time.hour in [1, 2, 3]:
                    #  multiplier = 0.9
                    multiplier -= 0.1
                elif time.hour == 4:
                    # multiplier = 0.95
                    multiplier += 0.05
                elif time.hour in [5, 6, 7]:
                    # multiplier = 1
                    multiplier += 0.05
                elif time.hour in [8]:
                    # multiplier = 0.9
                    multiplier -= 0.1
                elif time.hour in [9, 10, 11, 12, 13]:
                    # multiplier = 0.8
                    multiplier -= 0.1
                elif time.hour in [14]:
                    #  multiplier = 0.95
                    multiplier += 0.15
                elif time.hour in [15]:
                    #  multiplier = 1.00
                    multiplier += 0.05
                elif time.hour in [16, 17, 18]:
                    #  multiplier = 1.1
                    multiplier += 0.1
                elif time.hour in [19]:
                    #  multiplier = 1.2
                    multiplier += 0.1
                elif time.hour in [20, 21]:
                    #  multiplier = 1.3
                    multiplier += 0.1
                elif time.hour in [22]:
                    #  multiplier = 1.2
                    multiplier -= 0.1
                elif time.hour in [23]:
                    #  multiplier = 1.1
                    multiplier -= 0.1
                elif time.hour in [23, 0]:
                    multiplier -= 0.1
                #  multiplier = 1.0
            # make more fluctuate values
            if np.random.randint(min_fluc_value, max_fluc_value) in [0, 1, 2, 3]:
                multiplier += 0.03
            else:
                multiplier -= 0.03
            priceForEnergy = round(multiplier * randomNumber / 1000, 4)
            if priceForEnergy > 1.0:
                if priceForEnergy > 1.2:
                    max_fluc_value = 15
                else:
                    max_fluc_value = 10
            elif priceForEnergy > 0.6:
                max_fluc_value = 8
            elif priceForEnergy < 0.3:
                max_fluc_value = 5
            elif priceForEnergy < 0.2:
                max_fluc_value = 3
 
            frame = pd.DataFrame({"datetime": [str(time)], "price": [priceForEnergy]})
            table = table.append(frame, ignore_index=True)
 
    return table
 