from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

storage_home_setups_list = [
    {   # 1. There are no photovoltaics, no surplus, no stored energy,
        # so its necessary to use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 10, 
            },
            "surpluses": {
                sources.GRID_SURPLUS: {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }
            }
        }
    },
    {   # 2.1. There are no photovoltaics, no surplus, 
        # but stored energy are enough to power every device (energy stored == energy demand)
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 15,
        "first_window": {
            "receiver_energy": 15,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 15,
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
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }
            }
        }
    },
    {   # 2.2. There are no photovoltaics, no surplus, 
        # but stored energy is enough to power every device (energy stored > energy demand)
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 15,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 10,
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
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 5,
                }
            }
        }
    },
    {   # 3. There are no photovoltaics, no surplus, stored energy is not enough to power every device, 
        # so its necessary to use also the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0,
        "initial_storage_charge_value": 9,
        "first_window": {
            "receiver_energy": 15,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 0,
                "energy_storage_used": 9,
                "public_grid_used": 6, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }
            }
        }
    },
    {   # 4.1. There are no photovoltaics, no stored energy, 
        # but surplus energy is enough to power every device (surplus == energy demand)
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 0,
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
        }
    },
    {   # 4.2.1. There are no photovoltaics, no stored energy, 
        # but surplus energy is enough to power every device and  (surplus > energy demand) and to charge energy storage
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 4,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 4.59983,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.BATTERY_CHARGING,
                    "surplus_total_value": 0.40017,
                    "surplus_iteration_value_transfered": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.59983,
                    "total_energy_in_storage": 0.59983,
                }
            }
        }
    },
     { 
        # 4.2.2. There is no photovoltaics, there is stored energy, 
        # surplus energy is enough to power every device and to charge energy storage
        "storage_capacity": 6,
        "storage_voltage": 24, 
        "initial_grid_surplus_value": 10,
        "initial_storage_charge_value": 2,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5.59983,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.BATTERY_CHARGING,
                    "surplus_total_value": 2.40017,
                    "surplus_iteration_value_transfered": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.59983,
                    "total_energy_in_storage": 2.59983,
                }
            }
        }
    },
    {
        # 4.3. There are no photovoltaics, energy storage fully charged, 
        # surplus energy is enough to power every device (surplus > energy demand)
        "storage_capacity": 6, # 6 [kWh]
        "storage_voltage": 24,
        "initial_grid_surplus_value": 15,
        "initial_storage_charge_value": 6, 
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                    "surplus_total_value": 7,
                    "surplus_iteration_value_transfered": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 6,
                }
            }
        }
    },
    {   # 5. There are no photovoltaics, no stored energy, surplus energy is not enough to power every device, 
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 0,
                "public_grid_used": 5, 
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
    {   # 6.1. There are no photovoltaics, but surplus energy and stored energy are enough to power every device
        # surplus energy + stored energy == energy demand
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 5,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 5,
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
        }
    },
    {   # 6.2. There are no photovoltaics, but surplus energy and stored energy are enough to power every device
        # surplus energy + stored energy > energy demand -> some of energy will remain in storage
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 7,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 5,
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
                    "total_energy_in_storage": 2,
                }
            }
        }
    },
    {   # 7. There are no photovoltaics, surplus energy, stored energy are not enough to power every device
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 1,
        "first_window": {
            "receiver_energy": 10,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 5,
                "energy_storage_used": 1,
                "public_grid_used": 4, 
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
    {   # 8.1. Photovoltaics is enough to power every device and to charge storage
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0, 
        "initial_storage_charge_value": 1,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 5.4,
            "sources": {
                "photovoltaics_used": 5.4,
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
                    "total_energy_in_storage": 1.4,
                }
            }
        }
    },
    {   # 8.2. Photovoltaics is enough to power every device and to charge storage, and to add to the surplus grid
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 2, 
        "initial_storage_charge_value": 1,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 10,
            "sources": {
                "photovoltaics_used": 5.59983,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 5.12013,
                    "surplus_iteration_value_transfered": 4.40017,
                    "energy_loss": 0.88003,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0.59983,
                    "total_energy_in_storage": 1.59983,
                }
            }
        }
    },
    {   # 9. Photovoltaics is not enough to power every device, there are no surplus energy, no stored energy,
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0, 
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 7,
            "generator_energy": 4,
            "sources": {
                "photovoltaics_used": 4,
                "grid_surplus_used": 0,
                "energy_storage_used": 0,
                "public_grid_used": 3, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }
            }
        }
    },
    {   # 10. Photovoltaics and stored energy are enough to power every device
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0, 
        "initial_storage_charge_value": 10,
        "first_window": {
            "receiver_energy": 7,
            "generator_energy": 4,
            "sources": {
                "photovoltaics_used": 4,
                "grid_surplus_used": 0,
                "energy_storage_used": 3,
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
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 7,
                }
            }
        }
    },
    {   # 11. Photovoltaics and stored energy are not enough to power every device,
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 0, 
        "initial_storage_charge_value": 2,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 1,
            "sources": {
                "photovoltaics_used": 1,
                "grid_surplus_used": 0,
                "energy_storage_used": 2,
                "public_grid_used": 2, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 0,
                }
            }
        }
    },
    {   # 12. Photovoltaics and surplus are enough to power every device
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 10, 
        "initial_storage_charge_value": 6,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 3,
            "sources": {
                "photovoltaics_used": 3,
                "grid_surplus_used": 2,
                "energy_storage_used": 0,
                "public_grid_used": 0, 
            },
            "surpluses": {
                sources.GRID_SURPLUS : {
                    "usage_type": EnergySurplusRaport.DEVICES_POWERING,
                    "surplus_total_value": 6,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                },
                sources.ENERGY_STORAGE : {
                    "iteration_energy_stored": 0,
                    "total_energy_in_storage": 6,
                }
            }
        }
    },
    {   # 13. Photovoltaics and surplus are not enough to power every device,
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 0,
        "first_window": {
            "receiver_energy": 8,
            "generator_energy": 1,
            "sources": {
                "photovoltaics_used": 1,
                "grid_surplus_used": 5,
                "energy_storage_used": 0,
                "public_grid_used": 2, 
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
        }
    },
    {   # 14. Photovoltaics, surplus and stored energy are enough to power every device
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 6.25, 
        "initial_storage_charge_value": 4,
        "first_window": {
            "receiver_energy": 8,
            "generator_energy": 1,
            "sources": {
                "photovoltaics_used": 1,
                "grid_surplus_used": 5,
                "energy_storage_used": 2,
                "public_grid_used": 0, 
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
                    "total_energy_in_storage": 2,
                }
            }
        }
    },
    {   # 14. Photovoltaics, surplus and stored energy are not enough to power every device
        # so its necessary to also use the public grid energy
        "storage_capacity": 6,
        "storage_voltage": 24,
        "initial_grid_surplus_value": 2, 
        "initial_storage_charge_value": 1,
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 1,
            "sources": {
                "photovoltaics_used": 1,
                "grid_surplus_used": 1.6,
                "energy_storage_used": 1,
                "public_grid_used": 1.4, 
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
        }
    },   
]  
