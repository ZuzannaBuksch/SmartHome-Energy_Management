from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

multiwindowed_photovoltaics_home_setups_list = [
    # { # EXCHANGE only is enough to power every device and charge storage;
    #   # in second interval charged storage is enough to power every device
    #     "storage_capacity": 6,
    #     "storage_voltage": 24,
    #     "initial_grid_surplus_value": 0,
    #     "initial_storage_charge_value": 0,
    #     "exchange_total_value": 10,
    #     "exchange_remained_value": 10,
    #     "windows": [
    #         { # FIRST TIME WINDOW
    #             "receiver_energy": 5,
    #             "generator_energy": 0,
    #             "sources": {
    #                 "photovoltaics_used": 0,
    #                 "exchange_energy_used": 5.0144,
    #                 "grid_surplus_used": 0,
    #                 "energy_storage_used": 0,
    #                 "public_grid_used": 0, 
    #                 },
    #             "surpluses": {
    #                 sources.GRID_SURPLUS : {
    #                     "usage_type": EnergySurplusRaport.TRANSFER,
    #                     "surplus_total_value": 0,
    #                     "energy_loss": 0,
    #                     "surplus_iteration_value_transfered": 0,
    #                     },
    #                 sources.ENERGY_STORAGE : {
    #                     "iteration_energy_stored": 0.0144,
    #                     "total_energy_in_storage": 0.0144,
    #                 }

    #             }
    #         },
    #         { #SECOND TIME WINDOW,  na giełdzie zostało 4.9856 - 0.0144 
    #             "receiver_energy": 4,
    #             "generator_energy": 0,
    #             "sources": {
    #                 "photovoltaics_used": 0,
    #                 "exchange_energy_used": 0.014,
    #                 "grid_surplus_used": 0,
    #                 "energy_storage_used": 0,
    #                 "public_grid_used": 0, 
    #                 },
    #             "surpluses": {
    #                 sources.GRID_SURPLUS : {
    #                     "usage_type": EnergySurplusRaport.TRANSFER,
    #                     "surplus_total_value": 0,
    #                     "surplus_iteration_value_transfered": 0,
    #                     },
    #                 sources.ENERGY_STORAGE : {
    #                     "iteration_energy_stored": 0.0144,
    #                     "total_energy_in_storage": 0.02879,
    #                 }

    #             }
    #         },

    #     ]
    # },



    # { # PHOTOVOLTAICS is enough to power every device and charge storage and to add to grid surplus;
    #   # in second interval again;
    #     "storage_capacity": 6,
    #     "storage_voltage": 24,
    #     "initial_grid_surplus_value": 0,
    #     "initial_storage_charge_value": 1,
    #     "exchange_total_value": 0,
    #     "exchange_remained_value": 0,
    #     "windows": [
    #         { # FIRST TIME WINDOW
    #             "receiver_energy": 5,
    #             "generator_energy": 7,
    #             "sources": {
    #                 "photovoltaics_used": 5.0144,
    #                 "exchange_energy_used": 0,
    #                 "grid_surplus_used": 0,
    #                 "energy_storage_used": 0,
    #                 "public_grid_used": 0, 
    #                 },
    #             "surpluses": {
    #                 sources.GRID_SURPLUS : {
    #                     "usage_type": EnergySurplusRaport.TRANSFER,
    #                     "surplus_total_value": 1.58848,
    #                     "energy_loss": 0.39712,
    #                     "surplus_iteration_value_transfered": 1.9856,
    #                     },
    #                 sources.ENERGY_STORAGE : {
    #                     "iteration_energy_stored": 0.0144,
    #                     "total_energy_in_storage": 0.0144,
    #                 }
    #             }
    #         },
    #         { #SECOND TIME WINDOW, 
    #             "receiver_energy": 5,
    #             "generator_energy": 7,
    #             "sources": {
    #                 "photovoltaics_used": 5.0144,
    #                 "exchange_energy_used": 0,
    #                 "grid_surplus_used": 0,
    #                 "energy_storage_used": 0,
    #                 "public_grid_used": 0, 
    #                 },
    #             "surpluses": {
    #                 sources.GRID_SURPLUS : {
    #                     "usage_type": EnergySurplusRaport.TRANSFER,
    #                     "surplus_total_value": 3.9712,
    #                     "energy_loss": 0.39712,
    #                     "surplus_iteration_value_transfered": 1.9856,
    #                     },
    #                 sources.ENERGY_STORAGE : {
    #                     "iteration_energy_stored": 0.0144,
    #                     "total_energy_in_storage": 0.0288,
    #                 }
    #             }
    #         },

    #     ]
    # },


]
