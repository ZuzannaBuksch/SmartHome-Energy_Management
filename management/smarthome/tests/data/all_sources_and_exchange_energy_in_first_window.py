from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

multiwindowed_all_sources_and_exchange_energy_in_first_window_home_setups_list = [
    {   # 5.3.3. Exchange energy only for the first time window
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 6,
        "exchange_total_value": 2,
        "exchange_remained_value": 2,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 5,
                "generator_energy": 7, # 2 nadwyżki
                "sources": {
                    "photovoltaics_used": 5,
                    "exchange_energy_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 3.2,
                        "energy_loss": 0.8,
                        "surplus_iteration_value_transfered": 4,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 6,
                    }
                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 7,
                "generator_energy": 7,
                "sources": {
                    "photovoltaics_used": 7,
                    "exchange_energy_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 3.2,
                        "energy_loss": 0.8,
                        "surplus_iteration_value_transfered":0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 6,
                    }
                }
            },

        ]
    },
]
