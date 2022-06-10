from datetime import date, datetime, timedelta
from .base_calc import BaseEnergyCalculator, is_energy_needed
from collections import defaultdict
from services.smart_home import SmartHomeStorageChargingAndUsageRaport, JobType, SmartHomeEnergyStorage

CURRENT_STORAGE_CHARGING_FACTOR = 0.1

class EnergyStorageCalculator(BaseEnergyCalculator):
    _start_datetime = None
    _end_datetime = None
    _storage_devices_data = None

    def store_energy_surplus(self, remaining_energy): # FUNKCJA DO ZAŁADOWANIA AKUMULATORA NADWYŻKĄ ENERGII
        print("remaining in storage is ", remaining_energy)
        for device, data in self._storage_devices_data.items():
            if remaining_energy<=0:
                break
            free_space = device.capacity - data.get("current_capacity")
            if free_space>0:
                energy_to_store = min(free_space, remaining_energy)
                energy_stored = self._calculate_storage_charge(device, energy_to_store)
                print("max_value to put into storage is ", self._storage_devices_data[device]["max_charge_value_in_time_interval"])

                self._storage_devices_data[device]["max_charge_value_in_time_interval"]-=energy_stored
                remaining_energy-=energy_stored
        return remaining_energy

    @is_energy_needed
    def calculate_energy_cover(self, energy_demand): # FUNKCJA DO UŻYCIA ENERGII Z AKUMULATORA DO ZASILENIA DOMU
        print("\nhirki  00")
        print(self._storage_devices_data)
        total_storage_energy_used, storage_cover = 0, energy_demand
        energy_demand = abs(energy_demand)

        for device, data in self._storage_devices_data.items():
            if storage_cover>=0:
                break

            is_energy_in_storage = data['current_capacity'] > 0
            if is_energy_in_storage:
                storage_energy_used = self._calculate_storage_usage(device, energy_demand)
                total_storage_energy_used += storage_energy_used
                storage_cover = storage_energy_used - energy_demand
                energy_demand-=storage_energy_used

        return total_storage_energy_used, storage_cover #informacja czy energii z magazynu wystarczyło na pokrycie wszystkiego
    
    def update_storage_params(self, start_date, end_date, measurements, raports):
        self._start_datetime = start_date
        self._end_datetime = end_date
        devices_data = self._initialize_device_energy_dicts([*measurements, *raports])
        for data in measurements:
            devices_data[data.device]["charge_state_raports"].append(data)
        for raport in raports:
            devices_data[raport.device]["usage_raports"].append(raport)
        self._storage_devices_data = devices_data

        self._update_max_charge_values_in_time_interval()
        self._update_current_storages_capacities()

    
    def _update_max_charge_values_in_time_interval(self):
        max_time_of_usage = (self._end_datetime - self._start_datetime).total_seconds() / 60.0 / 60 # (2022,5,10,17,00,0)-(2022,5,10,15,30,0)=1:30:00
        for device in self._storage_devices_data.keys():
            max_charge_val = self._calculate_charge_value(max_time_of_usage, device)
            self._storage_devices_data[device]["max_charge_value_in_time_interval"] = max_charge_val

    def _update_current_storages_capacities(self):
        for device in self._storage_devices_data.keys():
            latest_charge_val = self._get_device_current_capacity(device)
            self._storage_devices_data[device]["current_capacity"] = latest_charge_val

    def _calculate_charging_time(self, storage, capacity_to_charge):
        # the simplest solution is convert capacity of storage from [kWh] to [Ah], this make calculations easier
        charging_current = self._get_charging_current(storage)
        capacity_to_charge = float(self._KWh_to_Ah(capacity_to_charge, storage.battery_voltage))
        return capacity_to_charge / charging_current #[Ah] / [A] = [h]

    def _calculate_charge_value(self, time_interval, storage):
        charging_current = self._get_charging_current(storage)
        charge_val_in_time_interval = time_interval * charging_current #[h] * [A] = [Ah]
        return (charge_val_in_time_interval * storage.battery_voltage) / 1000 # ([Ah] * [V]) = [Wh] -> [Wh] / 1000 = [kWh]

    def _calculate_storage_charge(self, storage, energy_to_store):
        max_charge_value = self._storage_devices_data[storage]["max_charge_value_in_time_interval"]
        storage_energy_used = min(energy_to_store, max_charge_value)
        self._set_device_current_capacity(storage, storage_energy_used)
        return storage_energy_used

    def _calculate_storage_usage(self, device, energy_to_use):
        current_capacity = self._get_device_current_capacity(device)
        storage_energy_used = min(current_capacity, energy_to_use)
        print("używamy ze storage ", storage_energy_used)
        self._set_device_current_capacity(device, 0-storage_energy_used)
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

    def _set_device_current_capacity(self, storage_device, energy_used):
        current_capacity = self._get_device_current_capacity(storage_device)
        new_capacity = current_capacity+energy_used
        print(f"current capacity={current_capacity} + energy_used={energy_used}  =  new_capacity={new_capacity}")
        if new_capacity > current_capacity:
            job_type = JobType.CHARGING
        else: 
            job_type = JobType.USAGE
        self._create_new_storage_usage_raport(storage_device, self._start_datetime, self._end_datetime, job_type)
        self._storage_devices_data[storage_device]["current_capacity"] = new_capacity

    def _get_device_current_capacity(self, storage_device):
        current_capacity = self._storage_devices_data[storage_device]["current_capacity"] 
        if current_capacity:
            return current_capacity
        charge_state_raports =  self._storage_devices_data[storage_device]["charge_state_raports"]
        try:
            latest = max([elem.date for elem in charge_state_raports])
        except ValueError:
            latest = self._start_datetime
        return [elem for elem in charge_state_raports if elem.date==latest][0].charge_value

    def _KWh_to_Ah(self, powerKWh, voltage):
        powerWh = powerKWh * 1000  # [Wh] * 1000 = [kWh]
        # [Ah] = [Wh] * 1/[V]
        return powerWh / voltage 

    def _get_charging_current(self, storage_device):
        capacity_in_ah = self._KWh_to_Ah(storage_device.capacity, storage_device.battery_voltage)
        return capacity_in_ah * CURRENT_STORAGE_CHARGING_FACTOR

    def _initialize_device_energy_dicts(self, device_data):
        if self._storage_devices_data:
            return self._storage_devices_data

        devices_data = defaultdict(lambda: {})
        for data in device_data:
            devices_data[data.device] = {}
            devices_data[data.device]["charge_state_raports"] = []
            devices_data[data.device]["usage_raports"] = []
            devices_data[data.device]["current_capacity"] = None
            devices_data[data.device]["max_charge_value_in_time_interval"] = None

        return devices_data
