from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

multiwindowed_photovoltaics_storage_home_setups_list =[

    { # in first window photovoltaics+grid surplus are just enough to power devices and charge storage
      # in second interval charged storage is enough to power every device
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 3.25, # 2.6 will be stored
        "initial_storage_charge_value": 0,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 4,
                "generator_energy": 2,
                "sources": {
                    "photovoltaics_used": 2,
                    "grid_surplus_used": 2.59983,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.BATTERY_CHARGING,
                        "surplus_total_value": 0.00017,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.59983,
                        "total_energy_in_storage": 0.59983,
                    }

                }
            },
            { #SECOND TIME WINDOW,  na giełdzie zostało 4.9856 - 0.0144 
                "receiver_energy": 0.6,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "grid_surplus_used": 0.00017,
                    "energy_storage_used": 0.59983,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                        "surplus_total_value": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 0,
                    }

                }
            },

        ]
    },

 { # 1) checking if we have surplus from PV's this value charging our storage (for 100% or possible charge value)
    # and rest of remaining energy transfer to grid surplus
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 2,
        "initial_storage_charge_value": 5.8,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 4,
                "generator_energy": 10, # 10-4-0.2 = 5.8
                "sources": {
                    "photovoltaics_used": 4.2,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0,
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 6.24,
                        "energy_loss": 1.16,
                        "surplus_iteration_value_transfered": 5.8,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.2,
                        "total_energy_in_storage": 6,
                    }
                }
            },
            { #SECOND TIME WINDOW
                "receiver_energy": 2,
                "generator_energy": 3,
                "sources": {
                    "photovoltaics_used": 2,
                    "grid_surplus_used":0,
                    "energy_storage_used": 0,
                    "public_grid_used": 0,
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.TRANSFER,
                        "surplus_total_value": 7.04,
                        "surplus_iteration_value_transfered": 1,
                        "energy_loss": 0.2,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 6,
                    }
                }
            },
        ]
     },
     {
        "storage_capacity": 4,
        "storage_voltage": 27,
        "initial_grid_surplus_value":  0.4, # 0.32
        "initial_storage_charge_value": 0.1,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 2,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "grid_surplus_used": 0.32,
                    "energy_storage_used": 0.1,
                    "public_grid_used": 1.58, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                        "surplus_total_value": 0,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 0,
                    }

                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 0.276,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0,
                    "public_grid_used":  0.276, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                        "surplus_total_value": 0,
                        "surplus_iteration_value_transfered": 0,
                        "energy_loss": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 0,
                    }

                }
            },
        ]
    },{
        "storage_capacity": 4,
        "storage_voltage": 27,
        "initial_grid_surplus_value":  0.48, # 0.384
        "initial_storage_charge_value":0.728,
        "windows": [
            { # FIRST TIME WINDOW
                "receiver_energy": 0.0325,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "grid_surplus_used": 0.384,
                    "energy_storage_used": 0,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.BATTERY_CHARGING,
                        "surplus_total_value": 0,
                        "energy_loss": 0,
                        "surplus_iteration_value_transfered": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0.3515,
                        "total_energy_in_storage": 1.0795,
                    }

                }
            },
            { #SECOND TIME WINDOW, 
                "receiver_energy": 0.037,
                "generator_energy": 0,
                "sources": {
                    "photovoltaics_used": 0,
                    "grid_surplus_used": 0,
                    "energy_storage_used": 0.037,
                    "public_grid_used": 0, 
                    },
                "surpluses": {
                    sources.GRID_SURPLUS : {
                        "usage_type": EnergySurplusRaport.BATTERY_CHARGING,
                        "surplus_total_value": 0,
                        "surplus_iteration_value_transfered": 0,
                        "energy_loss": 0,
                        },
                    sources.ENERGY_STORAGE : {
                        "iteration_energy_stored": 0,
                        "total_energy_in_storage": 1.0425,
                    }

                }
            }
        ]
    }
]
 