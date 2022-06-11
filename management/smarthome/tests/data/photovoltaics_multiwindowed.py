from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

multiwindowed_photovoltaics_home_setups_list = [
    { # 
        "initial_grid_surplus_value": 0,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 4,
                "generator_energy": 5,
                "sources": {
                    "photovoltaics_used": 4,
                    "grid_surplus_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 0.8,
                        "energy_loss": 0.2,
                        "surplus_iteration_value_transfered": 1,
                        },
                }
            },
            { #SECOND TIME WINDOW,  na giełdzie zostało 4.9856 - 0.0144 
                "receiver_energy": 4,
                "generator_energy": 2,
                "sources": {
                    "photovoltaics_used": 2,
                    "grid_surplus_used": 0.8,
                    "public_grid_used": 1.2, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                        "surplus_total_value": 0,
                        "surplus_iteration_value_transfered": 0,
                        }
                }
            },

        ]
    },
]
