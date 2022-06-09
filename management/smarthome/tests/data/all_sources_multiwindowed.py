from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

multiwindowed_all_sources_home_setups_list = [
   {
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "exchange_total_value": 10,
        "exchange_remained_value": 10,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 5,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "exchange_energy_used": 5.59983,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 0,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.59983,
                        "total_energy_in_storage": 0.59983,
                    }

                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 4,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "exchange_energy_used": 4.40017,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.40017,
                        "total_energy_in_storage": 1,
                    }

                }
            },
            

        ]
    },
    { # PHOTOVOLTAICS is enough to power every device and charge storage and to add to grid surplus;
      # in second interval again;
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 1,
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 5,
                "generator_energy": 7,
                "sources": {
                    "photovoltaics_used": 5.59983,
                    "exchange_energy_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 1.120136,
                        "energy_loss": 0.280034,
                        "surplus_iteration_value_transfered": 1.40017,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.5998333333333333,
                        "total_energy_in_storage": 1.59983,
                    }
                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 5,
                "generator_energy": 7,
                "sources": {
                    "photovoltaics_used": 5.59983,
                    "exchange_energy_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 2.240272,
                        "energy_loss": 0.28003,
                        "surplus_iteration_value_transfered": 1.40017,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.5998333333333333,
                        "total_energy_in_storage": 2.19967,
                    }
                }
            },
        ]
    },
    {   # 5.3.1. 

        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 6,
        "exchange_total_value": 5,
        "exchange_remained_value": 5,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 5,
                "generator_energy": 4,
                "sources": {
                    "photovoltaics_used": 4,
                    "exchange_energy_used": 1,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 0,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 6,
                    }
                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 5,
                "generator_energy": 4,
                "sources": {
                    "photovoltaics_used": 4,
                    "exchange_energy_used": 1,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 0,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
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
