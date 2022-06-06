from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

exchange_home_setups_list = [
    { #PHOTOVOLTAICS + EXCHANGE are enough to power every device
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "exchange_total_value": 5,
        "exchange_remained_value": 5,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 5,
            "sources": {
                "photovoltaics_used": 5,
                "exchange_energy_used": 5,
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
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }

            }
        }
    },
        { #1) There are no photovoltaics, no surplus, no stored energy, we have exchange energy and it is enough to power
        #every devices
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "exchange_total_value": 8,
        "exchange_remained_value": 5,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "exchange_energy_used": 5,
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
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }

            }
        }
    },
    { #2) There are no photovoltaics, no surplus, no stored energy, we have exchange energy but it is not enough to power
        #every devices, so it is necessary to use public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "exchange_total_value": 8,
        "exchange_remained_value": 5,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "exchange_energy_used": 5,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 5, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }

            }
        }
    },
        { #16) We have photovoltaics, surplus, energy stored, exchange energy 
        #but it is not enough to power every devices, so it is necessary to also use public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 2, # 2* 0.8 = 1.6
        "initial_storage_charge_value": 2, #change in variable
        "exchange_total_value": 10,
        "exchange_remained_value": 2,
        "first_window": {
            "receiver_energy": 20,
            "generator_energy": 10, #sumaric: 15.6, we need 4.4
            "sources": {
                "photovoltaics_used": 10,
                "exchange_energy_used": 2,
                "grid_surplus_used": 1.6,
                "energy_storage_used": 2,
                "public_grid_used": 4.4, 
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
        }
    },
    { #x1) charging time of free space (energy) in storage is lower than 1 hour, and surplus from PV's is lower (or equal to) than free space in acu
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 5.7,
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.2,
            "sources": {
                "photovoltaics_used": 5.2,
                "exchange_energy_used": 0,
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
                    "iteration_energy_stored": 0.2,
                    "total_energy_in_storage": 5.9,
                }

            }
        }
    },
        { #x11) charging time of free space (energy) in storage is lower than 1 hour, and surplus from PV's + grid_surplus_value is lower (or equal to) than free space in acu 
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0.125,
        "initial_storage_charge_value": 5.7,
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.1,
            "sources": {
                "photovoltaics_used": 5.1,
                "exchange_energy_used": 0,
                "grid_surplus_used": 0.1,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.DEVICES_POWERING, #TODO this is wrong! we charging battery not supply devices!
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0.0,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.2,
                    "total_energy_in_storage": 5.9,
                }

            }
        }
    },
            { #x111) charging time of free space (energy) in storage is lower than 1 hour, and surplus from PV's + grid_surplus_value + exchange energy value is lower (or equal to) than free space in acu 
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0.125,
        "initial_storage_charge_value": 5.7,
        "exchange_total_value": 2,
        "exchange_remained_value": 0.1,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.1,
            "sources": {
                "photovoltaics_used": 5.1,
                "exchange_energy_used": 0.1,
                "grid_surplus_used": 0.1,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.DEVICES_POWERING, #TODO this is wrong! we charging battery not supply devices!
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0.0,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.3,
                    "total_energy_in_storage": 6,
                }

            }
        }
    },

        { #x2) charging time of free space (energy) in storage is lower than 1 hour, and surplus from PV's is greater than free space in acu
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 5.7,
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 7,
            "sources": {
                "photovoltaics_used": 5.3,
                "exchange_energy_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 1.36,
                    "surplus_iteration_value_transfered": 1.7,
                    "energy_loss": 0.34,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.3,
                    "total_energy_in_storage": 6,
                }

            }
        }
    },
    { #x22) charging time of free space (energy) in storage is lower than 1 hour, and surplus from PV's  + grid_surplus_value is greater than free space in acu
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 4,
        "initial_storage_charge_value": 5.7,
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.2,
            "sources": {
                "photovoltaics_used": 5.2,
                "exchange_energy_used": 0,
                "grid_surplus_used": 0.1,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.DEVICES_POWERING, #TODO this is wrong! we charging battery not supply devices!
                    "surplus_total_value": 3.1,
                    "surplus_iteration_value_transfered": 0.0,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.3,
                    "total_energy_in_storage": 6,
                }
            }
        }
    },
            { #x3) charging time of free space (energy) in storage is greater than 1 hour, and surplus from PV's is lower (or equal to) than possible charge value (0.6kWh)
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 5, #>0.6 kwh
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.4,
            "sources": {
                "photovoltaics_used": 5.4,
                "exchange_energy_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
                },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.4,
                    "total_energy_in_storage": 5.4,
                }

            }
        }
    },
            { #x4) charging time of free space (energy) in storage is greater than 1 hour, and surplus from PV's 
            #is greater than possible charge value (0.6kWh)
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 5, #>0.6 kwh
        "exchange_total_value": 0,
        "exchange_remained_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 8,
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
                    "surplus_total_value": 1.92013,
                    "surplus_iteration_value_transfered": 2.40017,
                    "energy_loss": 0.48003,
                    },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.59983,
                    "total_energy_in_storage": 5.59983,
                }

            }
        }
    },
     { #
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "exchange_total_value": 10,
        "exchange_remained_value": 5.01,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "exchange_energy_used": 5.01,
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
                    "iteration_energy_stored": 0.01,
                    "total_energy_in_storage": 0.01,
                }

            }
        }
    }
]  
