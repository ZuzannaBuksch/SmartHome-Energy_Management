from datetime import date, datetime, timedelta
from .base_calc import BaseEnergyCalculator, is_energy_needed
from collections import defaultdict
from services.smart_home import SmartHomeStorageChargingAndUsageRaport, JobType, SmartHomeEnergyStorage

CURRENT_STORAGE_CHARGING_FACTOR = 0.1

class EnergyStorageCalculator(BaseEnergyCalculator):
    _storage_measurements = {}
    _start_datetime = None
    _end_datetime = None
    
    def store_energy_surplus(self, remaining_energy): # FUNKCJA DO ZAŁADOWANIA AKUMULATORA NADWYŻKĄ ENERGII
        for device, data in self._storage_measurements.items():
            if remaining_energy<=0:
                break

            usages_raport = data.get('charge_state',[])
            latest_charge_state = self._get_latests_storage_charge_state(data.get('charge_state',[]))
            free_space = device.capacity - latest_charge_state.charge_value

            if free_space>0:
                energy_to_store = min(free_space, remaining_energy)
                energy_stored = self._calculate_storage_charge(device, energy_to_store, usages_raport)
                remaining_energy-=energy_stored

        return remaining_energy

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand): # FUNKCJA DO UŻYCIA ENERGII Z AKUMULATORA DO ZASILENIA DOMU
        total_storage_energy_used, storage_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        for device, data in self._storage_measurements.items():
            if storage_cover>=0:
                break
            charges_raport = data.get('charge_state',[])
            usages_raport = data.get('usage',[])
            latest_charge_state = self._get_latests_storage_charge_state(charges_raport)
            is_energy_in_storage = latest_charge_state.charge_value > 0

            if is_energy_in_storage:
                storage_energy_used = self._calculate_storage_usage(device, latest_charge_state.charge_value, energy_demand, usages_raport)
                total_storage_energy_used += storage_energy_used
                storage_cover = storage_energy_used - energy_demand
                energy_demand-=storage_energy_used

        return total_storage_energy_used, storage_cover #informacja czy energii z magazynu wystarczyło na pokrycie wszystkiego
    
    def update_energy_states_and_usages(self, measurements, raports):
        device_measurements = self._initialize_device_energy_dicts([*measurements, *raports])
        for data in measurements:
            device_measurements[data.device]["charge_state"].append(data)
        for raport in raports:
            device_measurements[raport.device]["usage"].append(raport)
        self._storage_measurements = device_measurements

    def update_dates_range(self, start_date:datetime, end_date:date):
        self._start_datetime = start_date
        self._end_datetime = end_date

    def _calculate_charging_time(self, storage, capacity_to_charge):
        # the simplest solution is convert capacity of storage from [kWh] to [Ah], this make calculations easier
        charging_current = self._get_charging_current(storage)
        capacity_to_charge = self._KWh_to_Ah(capacity_to_charge, storage.battery_voltage)
        return capacity_to_charge / charging_current #[Ah] / [A] = [h]

    def _calculate_charge_value(self, time_interval, storage):
        charging_current = self._get_charging_current(storage)
        charge_val_in_time_interval = time_interval * charging_current #[h] * [A] = [Ah]
        x= (charge_val_in_time_interval * storage.battery_voltage) / 1000 # ([Ah] * [V]) = [Wh] -> [Wh] / 1000 = [kWh]
        return x

    def _calculate_storage_charge(self, storage, energy_to_store, usages_raport):
        start_datetime = max(self._start_datetime, self._get_storage_availability_date(usages_raport))
        if start_datetime > self._end_datetime: #storage was busy all the time
            return 0 # so 0 energy could be stored

        required_time_of_usage = self._calculate_charging_time(storage, energy_to_store)
        max_time_of_usage = (self._end_datetime - start_datetime).total_seconds() / 60.0 / 60 # (2022,5,10,17,00,0)-(2022,5,10,15,30,0)=1:30:00
        if required_time_of_usage <= max_time_of_usage: #okno czasowe wystarczyło by pobrać/wsadzić całą niezbędną energię
            storage_energy_used = energy_to_store
            end_datetime = start_datetime + timedelta(hours=required_time_of_usage)
        else: #okno czasowe NIE wystarczyło by pobrać całą niezbędną energię
            storage_energy_used = self._calculate_charge_value(max_time_of_usage, storage)
            end_datetime = self._end_datetime

        self._create_new_storage_usage_raport(storage, start_datetime, end_datetime, JobType.CHARGING)
        return storage_energy_used

    def _calculate_storage_usage(self, device, current_storage_capacity, energy_to_use, usages_raport):
        start_datetime = max(self._start_datetime, self._get_storage_availability_date(usages_raport))
        if start_datetime > self._end_datetime: #storage was busy all the time
            return 0 # so 0 energy could be used

        storage_energy_used = min(current_storage_capacity,energy_to_use)
        self._create_new_storage_usage_raport(device, start_datetime, self._end_datetime, JobType.USAGE)
        return storage_energy_used

    def _create_new_storage_usage_raport(self, device, start, end, job_type):
        smart_storage = SmartHomeEnergyStorage(device.__dict__)
        raport = SmartHomeStorageChargingAndUsageRaport({"date_time_from": start, "date_time_to": end, "job_type": job_type})
        # smart_storage.push_raports([raport])

    def _get_storage_availability_date(self, usages_raports):
        try:
            return max([elem.date for elem in usages_raports])
        except ValueError:
            return self._start_datetime

    def _get_latests_storage_charge_state(self, charge_state_raports):
        try:
            latest = max([elem.date for elem in charge_state_raports])
        except ValueError:
            latest = self._start_datetime
        return [elem for elem in charge_state_raports if elem.date==latest][0]

    def _KWh_to_Ah(self, powerKWh, voltage):
        powerWh = powerKWh * 1000  # [Wh] * 1000 = [kWh]
        # [Ah] = [Wh] * 1/[V]
        return powerWh / voltage 

    def _get_charging_current(self, storage_device):
        return storage_device.capacity * CURRENT_STORAGE_CHARGING_FACTOR

    def _initialize_device_energy_dicts(self, device_data):
        device_measurements = defaultdict(lambda: {})
        for data in device_data:
            device_measurements[data.device] = {}
            device_measurements[data.device]["charge_state"] = []
            device_measurements[data.device]["usage"]= []

        return device_measurements
